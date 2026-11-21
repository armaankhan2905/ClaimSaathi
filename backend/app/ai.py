"""Thin wrapper around the Claude API for structured extraction.

Every call asks for JSON matching a Pydantic model (structured outputs), so callers get a
validated object back, never free text to parse. When no API key is configured, `get_ai()`
returns None and callers use their rule-based fallback ("basic mode").
"""

import logging
import os
from functools import lru_cache
from typing import TypeVar

import anthropic
from pydantic import BaseModel

from .config import get_settings

log = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)

# On a safety-classifier decline the API re-runs the request on a suitable fallback model
# within the same call, instead of the request just stopping.
_FALLBACK_BETA = "server-side-fallback-2026-07-01"


class AIError(Exception):
    """The AI step failed; the caller should fall back to basic mode."""


class AIClient:
    def __init__(self, client: anthropic.Anthropic, model: str):
        self._client = client
        self.model = model

    def extract(self, schema: type[T], *, system: str, prompt: str, max_tokens: int = 16000, effort: str = "medium") -> T:
        try:
            response = self._client.beta.messages.parse(
                model=self.model,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": prompt}],
                output_format=schema,
                output_config={"effort": effort},
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
        log.info("AI %s: %s in / %s out tokens", schema.__name__, response.usage.input_tokens, response.usage.output_tokens)
        return parsed


@lru_cache
def _client_for(key: str | None, model: str) -> AIClient:
    return AIClient(anthropic.Anthropic(api_key=key, max_retries=3, timeout=180.0), model)


def get_ai() -> AIClient | None:
    """The Claude client, or None when AI is switched off or no key is configured."""
    s = get_settings()
    key = s.anthropic_api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not s.ai_enabled or not key:
        return None
    return _client_for(key, s.ai_model)
