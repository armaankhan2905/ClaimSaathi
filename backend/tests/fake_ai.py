"""A stand-in for AIClient so tests never call the real API."""

from collections.abc import Callable

from pydantic import BaseModel


class FakeAI:
    provider = "fake"
    model = "fake-model"
    clause_batch_size = 12
    parallel_requests = 4
    prompt_budget_chars: int | None = None

    def __init__(self, responder: Callable[[type[BaseModel], str], BaseModel]):
        self.responder = responder
        self.calls: list[tuple[str, str]] = []

    def extract(self, schema, *, system: str, prompt: str, max_tokens: int = 16000, effort: str = "medium"):
        self.calls.append((schema.__name__, prompt))
        return self.responder(schema, prompt)
