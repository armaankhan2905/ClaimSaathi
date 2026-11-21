import json
from types import SimpleNamespace

import pytest

from app import ai
from app.ai import GroqAIClient, _TokenBudget, strict_json_schema
from app.config import get_settings
from app.understanding.clauses import SplitClause
from app.understanding.labels import ClauseLabels, label_clauses
from app.understanding.terms import PolicyTerms, condensed_wording, extract_terms

from .fake_ai import FakeAI


def _walk(node):
    if isinstance(node, dict):
        yield node
        for v in node.values():
            yield from _walk(v)
    elif isinstance(node, list):
        for v in node:
            yield from _walk(v)


def test_strict_schema_rules():
    schema = strict_json_schema(PolicyTerms)
    assert "$defs" not in json.dumps(schema) and "$ref" not in json.dumps(schema)
    for node in _walk(schema):
        assert "default" not in node
        if node.get("type") == "object" and "properties" in node:
            assert node["additionalProperties"] is False
            assert set(node["required"]) == set(node["properties"])
    # optional fields stay nullable
    assert {"type": "null"} in schema["properties"]["sum_insured"]["anyOf"]
    wp = schema["properties"]["waiting_periods"]["items"]
    assert wp["properties"]["counted_from"]["enum"] == ["first_policy_date", "policy_start", "unclear"]


def _groq_sdk(content, finish="stop", total_tokens=900):
    calls = {}

    def create(**kwargs):
        calls.update(kwargs)
        return SimpleNamespace(
            choices=[SimpleNamespace(finish_reason=finish, message=SimpleNamespace(content=content))],
            usage=SimpleNamespace(total_tokens=total_tokens),
        )

    return SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create))), calls


def test_groq_request_shape_and_parsing():
    sdk, calls = _groq_sdk(json.dumps({"items": [{"ref": "4.2", "category": "waiting_period", "plain_en": "e", "plain_hi": "h", "plain_hn": "n"}]}))
    result = GroqAIClient(sdk, "openai/gpt-oss-120b", 8000).extract(ClauseLabels, system="sys", prompt="p", effort="low")
    assert result.items[0].ref == "4.2"
    fmt = calls["response_format"]
    assert fmt["type"] == "json_schema" and fmt["json_schema"]["strict"] is True and fmt["json_schema"]["name"] == "ClauseLabels"
    assert calls["reasoning_effort"] == "low" and calls["include_reasoning"] is False
    assert calls["max_completion_tokens"] <= 4000
    assert calls["messages"][0] == {"role": "system", "content": "sys"}


@pytest.mark.parametrize("content,finish,code", [("{}", "length", "too_long"), ("not json", "stop", "bad_output"), ('{"items": [{"ref": 1}]}', "stop", "bad_output")])
def test_groq_bad_responses(content, finish, code):
    sdk, _ = _groq_sdk(content, finish)
    with pytest.raises(ai.AIError, match=code):
        GroqAIClient(sdk, "m", 8000).extract(ClauseLabels, system="", prompt="")


def test_token_budget_waits_for_the_window_to_free_up():
    now = [0.0]
    slept = []

    def sleep(s):
        slept.append(s)
        now[0] += s

    budget = _TokenBudget(8000, clock=lambda: now[0], sleep=sleep)
    first = budget.reserve(5000)
    budget.settle(first, 6000)  # used more than estimated
    budget.reserve(1500)  # 7500 so far: fits without waiting
    assert slept == []
    budget.reserve(3000)  # would make 10500 > 8000: waits until the first one is a minute old
    assert slept and now[0] >= 60


def test_get_ai_picks_provider(monkeypatch):
    s = get_settings()
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.setattr(s, "groq_api_key", None)
    assert ai.get_ai() is None
    monkeypatch.setattr(s, "anthropic_api_key", "sk-ant-test")
    assert ai.get_ai().provider == "anthropic"
    monkeypatch.setattr(s, "groq_api_key", "gsk-test")
    assert ai.get_ai().provider == "groq"  # auto prefers Groq when both are set
    monkeypatch.setattr(s, "ai_provider", "anthropic")
    assert ai.get_ai().provider == "anthropic"
    monkeypatch.setattr(s, "ai_provider", "groq")
    monkeypatch.setattr(s, "groq_api_key", None)
    assert ai.get_ai() is None  # asked for Groq but no Groq key


def _clause(order, ref, title, section, text):
    return SplitClause(ref=ref, title=title, text=text, section_ref=ref.split(".")[0], section_title=section, page_start=1, page_end=1, order=order)


CLAUSES = [
    _clause(0, "1", "Preamble", "Preamble", "x" * 400),
    _clause(1, "3.1", "In-patient care", "What is covered", "y" * 400),
    _clause(2, "4.2", "Specified illnesses", "Waiting periods", "Joint replacement after 24 months from the First Policy Date."),
    _clause(3, "6", "Co-payment", "Co-payment", "10% outside network."),
]


def test_condensed_wording_keeps_important_clauses_in_order():
    text = condensed_wording(CLAUSES, budget=250)
    assert text.startswith("4.2 Specified illnesses") and "6 Co-payment" in text
    assert "Preamble" not in text and "In-patient" not in text


def test_groq_style_client_gets_condensed_prompt_and_small_batches():
    prompts = []

    def respond(schema, prompt):
        prompts.append((schema.__name__, prompt))
        if schema is PolicyTerms:
            return PolicyTerms()
        return ClauseLabels(items=[])

    fake = FakeAI(respond)
    fake.prompt_budget_chars, fake.clause_batch_size, fake.parallel_requests = 300, 2, 1
    extract_terms("Policy Schedule\nSum Insured Rs. 5,00,000", "\n".join(c.text for c in CLAUSES), CLAUSES, fake)
    terms_prompt = prompts[0][1]
    assert "4.2 Specified illnesses" in terms_prompt and "xxxx" not in terms_prompt
    label_clauses(CLAUSES, fake)
    assert sum(1 for name, _ in prompts if name == "ClauseLabels") == 2  # 4 clauses in batches of 2
