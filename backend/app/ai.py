"""AI providers for structured extraction: Claude (Anthropic) and Groq.

Every call asks for JSON matching a Pydantic model, so callers get a validated object back,
never free text to parse. `get_ai()` picks a provider from the configured keys, or returns
None, in which case callers use their rule-based fallback ("basic mode").

Each client also says how work should be sized for it: how many clauses per request, how many
requests at once, and how long a prompt may be (Groq's free plan allows 8K tokens a minute).
"""

import json
import logging
import os
import threading
import time
from collections import deque
from functools import lru_cache
from typing import Protocol, TypeVar

from pydantic import BaseModel, ValidationError

from .config import get_settings

log = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


class AIError(Exception):
    """The AI step failed; the caller should fall back to basic mode."""


class AIClientProtocol(Protocol):
    provider: str
    model: str
    clause_batch_size: int  # clauses explained per request
    parallel_requests: int  # requests that may run at the same time
    prompt_budget_chars: int | None  # longest prompt to send (None = no limit)

    def extract(self, schema: type[T], *, system: str, prompt: str, max_tokens: int = 16000, effort: str = "medium") -> T: ...


# --------------------------------------------------------------------------- Claude

_FALLBACK_BETA = "server-side-fallback-2026-07-01"


class AIClient:
    """Claude via the Anthropic SDK (structured outputs + server-side refusal fallback)."""

    provider = "anthropic"
    clause_batch_size = 12
    parallel_requests = 4
    prompt_budget_chars = None

    def __init__(self, client, model: str):
        self._client = client
        self.model = model

    def extract(self, schema: type[T], *, system: str, prompt: str, max_tokens: int = 16000, effort: str = "medium") -> T:
        import anthropic

        try:
            response = self._client.beta.messages.parse(
                model=self.model,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": prompt}],
                output_format=schema,
                output_config={"effort": effort},
                # On a safety-classifier decline the API re-runs the request on a fallback model.
                betas=[_FALLBACK_BETA],
                fallbacks="default",
            )
        except anthropic.APIConnectionError as e:
            raise AIError("connection") from e
        except anthropic.AuthenticationError as e:
            raise AIError("auth") from e
        except anthropic.RateLimitError as e:
            raise AIError("rate_limited") from e
        except anthropic.APIStatusError as e:
            raise AIError(f"api_{e.status_code}") from e

        if response.stop_reason == "refusal":
            raise AIError("refusal")
        if response.stop_reason == "max_tokens":
            raise AIError("too_long")
        parsed = response.parsed_output
        if parsed is None:
            raise AIError("no_output")
        log.info("Claude %s: %s in / %s out tokens", schema.__name__, response.usage.input_tokens, response.usage.output_tokens)
        return parsed


# --------------------------------------------------------------------------- Groq


def strict_json_schema(model: type[BaseModel]) -> dict:
    """Pydantic schema -> the form Groq's strict mode accepts: every property required (optional
    ones stay nullable), no extra properties, no defaults, and $refs inlined."""
    schema = model.model_json_schema()
    defs = schema.pop("$defs", {})

    def fix(node):
        if isinstance(node, dict):
            if "$ref" in node:
                return fix(dict(defs[node["$ref"].split("/")[-1]]))
            node = {k: fix(v) for k, v in node.items() if k not in ("default", "title")}
            if node.get("type") == "object" and "properties" in node:
                node["required"] = list(node["properties"])
                node["additionalProperties"] = False
            return node
        if isinstance(node, list):
            return [fix(n) for n in node]
        return node

    return fix(schema)


class _TokenBudget:
    """Waits before a request that would push usage over the per-minute token limit, so the
    free plan's 8K tokens/minute is respected instead of hitting 429 errors."""

    def __init__(self, per_minute: int, clock=time.monotonic, sleep=time.sleep):
        self.per_minute = per_minute
        self._entries: deque[list] = deque()  # [timestamp, tokens]
        self._lock = threading.Lock()
        self._clock, self._sleep = clock, sleep

    def _used_last_minute(self, now: float) -> int:
        while self._entries and now - self._entries[0][0] > 60:
            self._entries.popleft()
        return sum(e[1] for e in self._entries)

    def reserve(self, tokens: int) -> list:
        """Blocks until `tokens` fit in the last minute's budget; returns the reservation."""
        tokens = min(tokens, self.per_minute)
        while True:
            with self._lock:
                now = self._clock()
                if self._used_last_minute(now) + tokens <= self.per_minute:
                    entry = [now, tokens]
                    self._entries.append(entry)
                    return entry
                wait = 60 - (now - self._entries[0][0]) + 0.5
            self._sleep(max(0.5, wait))

    def settle(self, entry: list, actual: int) -> None:
        """Replace the estimate with what the request really used."""
        with self._lock:
            entry[1] = actual


class GroqAIClient:
    """Open models on Groq (free plan available). Strict JSON-schema outputs on gpt-oss."""

    provider = "groq"
    clause_batch_size = 4
    parallel_requests = 1
    prompt_budget_chars = 14000  # about 3.5K tokens, leaving room for the answer within 8K/minute

    def __init__(self, client, model: str, tokens_per_minute: int):
        self._client = client
        self.model = model
        self._budget = _TokenBudget(tokens_per_minute)

    def extract(self, schema: type[T], *, system: str, prompt: str, max_tokens: int = 16000, effort: str = "medium") -> T:
        import groq

        max_out = min(max_tokens, 4000)
        estimated = (len(system) + len(prompt)) // 3 + max_out
        reservation = self._budget.reserve(estimated)
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
                response_format={
                    "type": "json_schema",
                    "json_schema": {"name": schema.__name__, "strict": True, "schema": strict_json_schema(schema)},
                },
                reasoning_effort=effort if effort in ("low", "medium", "high") else "medium",
                include_reasoning=False,
                max_completion_tokens=max_out,
                temperature=0.2,
            )
        except groq.APIConnectionError as e:
            raise AIError("connection") from e
        except groq.AuthenticationError as e:
            raise AIError("auth") from e
        except groq.RateLimitError as e:
            raise AIError("rate_limited") from e
        except groq.APIStatusError as e:
            raise AIError(f"api_{e.status_code}") from e

        usage = getattr(response, "usage", None)
        self._budget.settle(reservation, getattr(usage, "total_tokens", None) or estimated)
        choice = response.choices[0]
        if choice.finish_reason == "length":
            raise AIError("too_long")
        try:
            parsed = schema.model_validate(json.loads(choice.message.content or ""))
        except (json.JSONDecodeError, ValidationError) as e:
            raise AIError("bad_output") from e
        log.info("Groq %s: %s tokens", schema.__name__, getattr(usage, "total_tokens", "?"))
        return parsed


# --------------------------------------------------------------------------- choosing


@lru_cache
def _anthropic_client(key: str, model: str) -> AIClient:
    import anthropic

    return AIClient(anthropic.Anthropic(api_key=key, max_retries=3, timeout=180.0), model)


@lru_cache
def _groq_client(key: str, model: str, tpm: int) -> GroqAIClient:
    import groq

    # The SDK retries 429s itself, waiting as long as Groq's retry-after header says.
    return GroqAIClient(groq.Groq(api_key=key, max_retries=6, timeout=120.0), model, tpm)


def get_ai() -> AIClientProtocol | None:
    """The configured AI client, or None when AI is switched off or no key is set."""
    s = get_settings()
    if not s.ai_enabled:
        return None
    groq_key = s.groq_api_key or os.environ.get("GROQ_API_KEY")
    anthropic_key = s.anthropic_api_key or os.environ.get("ANTHROPIC_API_KEY")
    provider = s.ai_provider.lower()
    if provider in ("groq", "auto") and groq_key:
        return _groq_client(groq_key, s.groq_model, s.groq_tokens_per_minute)
    if provider in ("anthropic", "auto") and anthropic_key:
        return _anthropic_client(anthropic_key, s.ai_model)
    return None
