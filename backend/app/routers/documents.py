import hashlib
import re
from urllib.parse import quote

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, Response, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from .. import storage
from ..config import get_settings
from ..db import get_db, get_session_factory
from ..deps import current_user
from ..documents import delete_document_files, process_document
from ..extraction import sniff_content_type
from ..models import Document, User
from ..schemas import DocumentKind, DocumentOut, DocumentPageOut
from .policies import get_owned_policy

router = APIRouter(prefix="/api/documents", tags=["documents"])

# Error details are short codes; the frontend shows a translated message for each.


def _get_owned_document(document_id: int, user: User, db: Session) -> Document:
    doc = db.get(Document, document_id)
    if doc is None or doc.owner_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "document_not_found")
    return doc


def _clean_filename(name: str | None) -> str:
    name = (name or "document").replace("\\", "/").rsplit("/", 1)[-1]
    name = re.sub(r"[\x00-\x1f\x7f]", "", name).strip() or "document"
    return name[:255]


@router.post("", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def upload_document(
    background: BackgroundTasks,
    file: UploadFile = File(...),
    kind: DocumentKind = Form(...),
    policy_id: int | None = Form(None),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
    session_factory: sessionmaker = Depends(get_session_factory),
) -> Document:
    if policy_id is not None:
        get_owned_policy(policy_id, user, db)

    limit = get_settings().max_upload_mb * 1024 * 1024
    data = await file.read(limit + 1)
    if len(data) > limit:
        raise HTTPException(status.HTTP_413_CONTENT_TOO_LARGE, "file_too_large")
    if not data:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "empty_file")
    content_type = sniff_content_type(data)
    if content_type is None:
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "unsupported_type")

    doc = Document(
        owner_id=user.id,
        policy_id=policy_id,
        kind=kind,
        filename=_clean_filename(file.filename),
        content_type=content_type,
        size_bytes=len(data),
        sha256=hashlib.sha256(data).hexdigest(),
        storage_key=storage.save(data),
        status="processing",
    )
    db.add(doc)
    db.commit()
    background.add_task(process_document, doc.id, session_factory)
    return doc


@router.get("", response_model=list[DocumentOut])
def list_documents(
    policy_id: int | None = None, user: User = Depends(current_user), db: Session = Depends(get_db)
) -> list[Document]:
    q = select(Document).where(Document.owner_id == user.id)
    if policy_id is not None:
        q = q.where(Document.policy_id == policy_id)
    return list(db.scalars(q.order_by(Document.created_at.desc(), Document.id.desc())))


@router.get("/{document_id}", response_model=DocumentOut)
def get_document(document_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)) -> Document:
    return _get_owned_document(document_id, user, db)


@router.get("/{document_id}/pages", response_model=list[DocumentPageOut])
def get_pages(document_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return _get_owned_document(document_id, user, db).pages


@router.get("/{document_id}/file")
def download_file(document_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)) -> Response:
    doc = _get_owned_document(document_id, user, db)
    return Response(
        content=storage.load(doc.storage_key),
        media_type=doc.content_type,
        headers={
            "Content-Disposition": f"inline; filename*=UTF-8''{quote(doc.filename)}",
            "Cache-Control": "private, no-store",
            "X-Content-Type-Options": "nosniff",
        },
    )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)) -> Response:
    doc = _get_owned_document(document_id, user, db)
    delete_document_files([doc])
    db.delete(doc)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
