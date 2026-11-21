"""Background processing of uploaded documents: decrypt, read, store page text, then hand
policy documents on to policy understanding."""

import logging

from sqlalchemy.orm import sessionmaker

from . import storage
from .extraction import ExtractionError, extract
from .models import Document, DocumentPage
from .understanding.pipeline import after_document_read, understand_policy

log = logging.getLogger(__name__)


def process_document(document_id: int, session_factory: sessionmaker) -> None:
    with session_factory() as db:
        doc = db.get(Document, document_id)
        if doc is None:  # deleted before processing started
            return
        error = None
        try:
            pages = extract(storage.load(doc.storage_key), doc.content_type)
        except ExtractionError as e:
            error = e.code
        except Exception:
            log.exception("Reading document %s failed", document_id)
            error = "internal_error"

        if db.get(Document, document_id) is None:  # deleted while we were reading
            return
        if error:
            doc.status, doc.error = "failed", error
            db.commit()
            # Don't leave its policy waiting for a document that will never be ready.
            if doc.policy_id is not None:
                _safely(understand_policy, doc.policy_id, session_factory)
            return

        doc.pages = [
            DocumentPage(page_number=p.number, text=p.text, method=p.method, ocr_confidence=p.confidence) for p in pages
        ]
        doc.page_count = len(pages)
        doc.ocr_pages = sum(p.method == "ocr" for p in pages)
        doc.status = "ready"
        doc.error = None
        db.commit()
    _safely(after_document_read, document_id, session_factory)


def _safely(step, target_id: int, session_factory: sessionmaker) -> None:
    # A failure in understanding must not affect the document, which was read and saved.
    try:
        step(target_id, session_factory)
    except Exception:
        log.exception("%s(%s) failed", step.__name__, target_id)


def delete_document_files(docs: list[Document]) -> None:
    for d in docs:
        storage.delete(d.storage_key)
