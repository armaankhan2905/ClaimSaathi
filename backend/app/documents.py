"""Background processing of uploaded documents: decrypt, read, store page text."""

import logging

from sqlalchemy.orm import Session, sessionmaker

from . import storage
from .extraction import ExtractionError, extract
from .models import Document, DocumentPage

log = logging.getLogger(__name__)


def process_document(document_id: int, session_factory: sessionmaker) -> None:
    with session_factory() as db:
        doc = db.get(Document, document_id)
        if doc is None:  # deleted before processing started
            return
        try:
            pages = extract(storage.load(doc.storage_key), doc.content_type)
        except ExtractionError as e:
            _fail(db, doc, e.code)
            return
        except Exception:
            log.exception("Reading document %s failed", document_id)
            _fail(db, doc, "internal_error")
            return

        if db.get(Document, document_id) is None:  # deleted while we were reading
            return
        doc.pages = [
            DocumentPage(page_number=p.number, text=p.text, method=p.method, ocr_confidence=p.confidence) for p in pages
        ]
        doc.page_count = len(pages)
        doc.ocr_pages = sum(p.method == "ocr" for p in pages)
        doc.status = "ready"
        doc.error = None
        db.commit()


def _fail(db: Session, doc: Document, code: str) -> None:
    doc.status = "failed"
    doc.error = code
    db.commit()


def delete_document_files(docs: list[Document]) -> None:
    for d in docs:
        storage.delete(d.storage_key)
