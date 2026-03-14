"""JSON-based memory store — DeerFlow-compatible pattern."""

import json
from datetime import UTC, datetime
from pathlib import Path


class MemoryStore:
    """Persist and retrieve conversational facts as a JSON file.

    Follows DeerFlow's memory.json pattern:
    - Facts extracted from conversations with confidence scores
    - Top-N injection into system prompt
    - Atomic file writes
    """

    def __init__(self, path: Path, max_facts: int = 50, inject_limit: int = 15):
        self.path = path
        self.max_facts = max_facts
        self.inject_limit = inject_limit
        self._facts: list[dict] = []
        self._load()

    def get_context(self) -> str:
        """Format top facts as a natural-language context block."""
        if not self._facts:
            return ""
        top = self._ranked_facts(self.inject_limit)
        lines = [f"- {f['content']}" for f in top]
        return "Relevant context from previous interactions:\n" + "\n".join(lines)

    def add_facts(self, facts: list[dict]) -> None:
        """Append new facts and trim to max capacity."""
        self._facts.extend(facts)
        self._trim()
        self._save()

    def _ranked_facts(self, limit: int) -> list[dict]:
        return sorted(
            self._facts,
            key=lambda f: f.get("confidence", 0.5),
            reverse=True,
        )[:limit]

    def _trim(self) -> None:
        if len(self._facts) > self.max_facts:
            self._facts = self._ranked_facts(self.max_facts)

    def _load(self) -> None:
        if self.path.exists():
            data = json.loads(self.path.read_text(encoding="utf-8"))
            self._facts = data.get("facts", [])

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "facts": self._facts,
            "updated_at": datetime.now(UTC).isoformat(),
        }
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.rename(self.path)
