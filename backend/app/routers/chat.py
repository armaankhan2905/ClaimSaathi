from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from ..ai import get_ai
from ..db import get_db
from ..deps import current_user
from ..models import ChatMessage, User
from ..schemas import AskIn, ChatMessageOut
from ..understanding.ask import ClauseView, answer_question
from .policies import get_owned_policy

router = APIRouter(prefix="/api/policies", tags=["ask"])

MAX_MESSAGES = 200  # per policy; the oldest are dropped beyond this


@router.get("/{policy_id}/chat", response_model=list[ChatMessageOut])
def get_chat(policy_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return get_owned_policy(policy_id, user, db).chat


@router.post("/{policy_id}/chat", response_model=list[ChatMessageOut])
def ask(policy_id: int, body: AskIn, user: User = Depends(current_user), db: Session = Depends(get_db)) -> list[ChatMessage]:
    """Answer a question about this policy from its own clauses. Returns the question and the answer."""
    policy = get_owned_policy(policy_id, user, db)
    if not policy.clauses:
        raise HTTPException(status.HTTP_409_CONFLICT, "no_clauses")

    history = [{"role": m.role, "content": m.content} for m in policy.chat[-6:]]
    clauses = [ClauseView(c.id, c.ref, c.title, c.section_title, c.text, c.category, c.plain, c.embedding) for c in policy.clauses]
    result = answer_question(body.question.strip(), body.lang, clauses, policy.terms, history, get_ai())

    question = ChatMessage(role="user", content=body.question.strip(), lang=body.lang)
    answer = ChatMessage(
        role="assistant",
        content=result.answer,
        lang=body.lang,
        answer_type=result.answer_type,
        citations=result.citations,
        follow_ups=result.follow_ups,
        mode=result.mode,
    )
    policy.chat.extend([question, answer])
    overflow = len(policy.chat) - MAX_MESSAGES
    if overflow > 0:
        del policy.chat[:overflow]  # removed from the list = deleted (delete-orphan)
    db.commit()
    return [question, answer]


@router.delete("/{policy_id}/chat", status_code=status.HTTP_204_NO_CONTENT)
def clear_chat(policy_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)) -> Response:
    policy = get_owned_policy(policy_id, user, db)
    policy.chat = []
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
