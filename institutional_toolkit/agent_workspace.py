"""Country-scoped evidence request orchestration for Road Safety Intelligence Agent.

All factual generation uses only the existing country-filtered RAG corpus.
No Web search, no global fallback, and no automatic ingestion of updates.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from . import rag


@dataclass(frozen=True)
class AgentRequest:
    primary_country: str
    question: str
    comparison_country: str | None = None

    def validate(self, countries: list[str]) -> None:
        if self.primary_country not in countries:
            raise ValueError("The first selected country is not in the country directory.")
        if self.comparison_country is not None:
            if self.comparison_country not in countries or self.comparison_country == self.primary_country:
                raise ValueError("Select a different, supported comparison country.")
        if not 8 <= len(self.question.strip()) <= 550:
            raise ValueError("Enter a specific question between 8 and 550 characters.")

    @property
    def label(self) -> str:
        if self.comparison_country:
            return f"{self.primary_country} vs {self.comparison_country}"
        return self.primary_country


def retrieve_request(data: dict, request: AgentRequest, data_dir: str | Path,
                     max_per_country: int = 6) -> dict[str, Any]:
    """Strict jurisdiction selection happens independently of the prompt text."""
    request.validate(data["countries"])
    if request.comparison_country:
        hits = rag.retrieve_pair(data, request.primary_country, request.comparison_country,
                                 request.question, data_dir=data_dir, per_country=max_per_country)
    else:
        hits = rag.retrieve(data, request.primary_country, request.question,
                            data_dir=data_dir, limit=min(12, max_per_country * 2))
    counts = {request.primary_country: sum(h["country"] == request.primary_country for h in hits)}
    if request.comparison_country:
        counts[request.comparison_country] = sum(h["country"] == request.comparison_country for h in hits)
    # For pairwise claims, showing one-sided AI answers as a comparison would
    # be misleading. The UI may still display the available original sources.
    comparable = bool(hits) and all(counts.values())
    return {
        "scope": "compare" if request.comparison_country else "country",
        "first": request.primary_country,
        "second": request.comparison_country,
        "label": request.label,
        "question": request.question.strip(),
        "hits": hits,
        "counts": counts,
        "sufficient_for_ai": comparable,
        "result": None,
        "status": ("Evidence ready" if comparable else
                   "Evidence incomplete for both countries" if request.comparison_country else
                   "No matching source-linked evidence"),
    }


def ask(data: dict, request: AgentRequest, data_dir: str | Path, *,
        run_ai: bool, max_per_country: int = 6, client=None) -> dict[str, Any]:
    """One-click retrieval and, if configured, citation-locked synthesis.

    A provided client supports deterministic offline tests. Never call the
    model for countries without source-linked retrieval coverage.
    """
    payload = retrieve_request(data, request, data_dir, max_per_country)
    if run_ai and payload["sufficient_for_ai"]:
        payload["result"] = rag.synthesis(request.question, payload["hits"], client=client)
    return payload
