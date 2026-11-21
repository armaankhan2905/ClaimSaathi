from types import SimpleNamespace

import anthropic
import httpx2
import pytest
from pydantic import BaseModel

from app import ai
from app.config import get_settings


class Answer(BaseModel):
    value: str


def _fake_sdk(response=None, error=None):
    calls = {}

    def parse(**kwargs):
        calls.update(kwargs)
        if error:
            raise error
        return response

    client = SimpleNamespace(beta=SimpleNamespace(messages=SimpleNamespace(parse=parse)))
    return client, calls


def _response(stop_reason="end_turn", parsed=Answer(value="ok")):
    return SimpleNamespace(stop_reason=stop_reason, parsed_output=parsed, usage=SimpleNamespace(input_tokens=10, output_tokens=5))


def test_get_ai_none_without_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(get_settings(), "anthropic_api_key", None)
    assert ai.get_ai() is None


def test_get_ai_respects_switch(monkeypatch):
    monkeypatch.setattr(get_settings(), "anthropic_api_key", "sk-test")
    monkeypatch.setattr(get_settings(), "ai_enabled", False)
    assert ai.get_ai() is None
    monkeypatch.setattr(get_settings(), "ai_enabled", True)
    assert ai.get_ai().model == get_settings().ai_model


def test_extract_sends_schema_effort_and_fallbacks():
    sdk, calls = _fake_sdk(_response())
    result = ai.AIClient(sdk, "claude-opus-5-5").extract(Answer, system="sys", prompt="hi", effort="low")
    assert result.value == "ok"
    assert calls["model"] == "claude-opus-5-5" and calls["output_format"] is Answer
    assert calls["output_config"] == {"effort": "low"}
    assert calls["fallbacks"] == "default" and calls["betas"] == ["server-side-fallback-2026-07-01"]


@pytest.mark.parametrize("stop,code", [("refusal", "refusal"), ("max_tokens", "too_long")])
def test_bad_stop_reasons_raise(stop, code):
    sdk, _ = _fake_sdk(_response(stop_reason=stop))
    with pytest.raises(ai.AIError, match=code):
        ai.AIClient(sdk, "m").extract(Answer, system="", prompt="")


def test_api_errors_become_ai_errors():
    req = httpx2.Request("POST", "https://api.anthropic.com/v1/messages")
    err = anthropic.RateLimitError("slow down", response=httpx2.Response(429, request=req), body=None)
    sdk, _ = _fake_sdk(error=err)
    with pytest.raises(ai.AIError, match="rate_limited"):
        ai.AIClient(sdk, "m").extract(Answer, system="", prompt="")
