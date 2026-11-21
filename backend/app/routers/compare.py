from collections import OrderedDict
from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..ai import get_ai
from ..db import get_db
from ..deps import current_user
from ..models import Policy, User
from ..schemas import CompareIn
from ..understanding.ask import ClauseView
from ..understanding.compare import SCENARIO_BY_KEY, SCENARIOS, evaluate, feature_table, month_from_text, winner
from .policies import get_owned_policy

router = APIRouter(prefix="/api/compare", tags=["compare"])

# Repeating a comparison shouldn't cost another AI call: results are kept until either policy is re-read.
_cache: OrderedDict[tuple, dict] = OrderedDict()
_CACHE_SIZE = 200


def _views(p: Policy) -> list[ClauseView]:
    return [ClauseView(c.id, c.ref, c.title, c.section_title, c.text, c.category, c.plain, c.embedding) for c in p.clauses]


def _pair(a: int, b: int, user: User, db: Session) -> tuple[Policy, Policy]:
    if a == b:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "same_policy")
    pa, pb = get_owned_policy(a, user, db), get_owned_policy(b, user, db)
    if not pa.clauses or not pb.clauses:
        raise HTTPException(status.HTTP_409_CONFLICT, "no_clauses")
    return pa, pb


@router.get("/scenarios")
def list_scenarios(category: str = Query("health")) -> list[dict]:
    return [{"key": s.key, "text": s.text, "month": s.month} for s in SCENARIOS if s.category == category]


@router.get("/table")
def compare_table(a: int, b: int, user: User = Depends(current_user), db: Session = Depends(get_db)) -> list[dict]:
    pa, pb = _pair(a, b, user, db)
    return feature_table(pa.terms, pb.terms, _views(pa), _views(pb))


@router.post("")
def compare_scenario(body: CompareIn, user: User = Depends(current_user), db: Session = Depends(get_db)) -> dict:
    """Test one situation against both policies."""
    pa, pb = _pair(body.a, body.b, user, db)
    if body.scenario:
        preset = SCENARIO_BY_KEY.get(body.scenario)
        if preset is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "unknown_scenario")
        text, month, keywords, key = preset.text, preset.month, preset.keywords, preset.key
    elif body.custom:
        text, month, keywords, key = body.custom.strip(), month_from_text(body.custom), (), None
    else:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "scenario_or_custom_required")

    ai = get_ai()
    cache_key = (pa.id, pa.analyzed_at, pb.id, pb.analyzed_at, text, month, body.lang, getattr(ai, "provider", None))
    if cache_key in _cache:
        _cache.move_to_end(cache_key)
        return _cache[cache_key]

    ra = evaluate(text, keywords, month, body.lang, _views(pa), pa.terms, ai)
    rb = evaluate(text, keywords, month, body.lang, _views(pb), pb.terms, ai)
    result = {
        "scenario": {"key": key, "text": text, "month": month},
        "a": {"policy_id": pa.id, **asdict(ra)},
        "b": {"policy_id": pb.id, **asdict(rb)},
        "winner": winner(ra, rb),
    }
    _cache[cache_key] = result
    if len(_cache) > _CACHE_SIZE:
        _cache.popitem(last=False)
    return result
