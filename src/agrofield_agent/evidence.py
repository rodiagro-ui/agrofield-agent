"""Request-local source references resolved only against the original note."""

from __future__ import annotations

import re
from dataclasses import dataclass


MAX_SOURCE_SPANS = 32


@dataclass(frozen=True)
class SourceSpan:
    start: int
    end: int


def source_spans(raw_text: str) -> dict[str, SourceSpan]:
    """Keep exact offsets, decimal numbers and at most 32 contiguous fragments."""
    boundaries = list(re.finditer(r"(?<=[.!?])\s+|\n+", raw_text))[
        : MAX_SOURCE_SPANS - 1
    ]
    spans: dict[str, SourceSpan] = {}
    start = 0
    for stop in [match.end() for match in boundaries] + [len(raw_text)]:
        end = stop
        while start < end and raw_text[start].isspace():
            start += 1
        while end > start and raw_text[end - 1].isspace():
            end -= 1
        if end > start:
            spans[f"S{len(spans) + 1:02d}"] = SourceSpan(start, end)
        start = stop
    return spans


def source_catalog(raw_text: str) -> dict[str, str]:
    return {
        source_id: raw_text[span.start:span.end]
        for source_id, span in source_spans(raw_text).items()
    }


def resolve_sources(source_ids: object, raw_text: str) -> str:
    """Return the smallest original excerpt covering the selected source spans.

    Multiple sentences retain the intervening original text and whitespace. The
    model cannot supply replacement text, offsets or references from another note.
    Reference validity proves provenance, not that a cited fact is true.
    """
    spans = source_spans(raw_text)
    if not isinstance(source_ids, list) or any(
        not isinstance(source_id, str) or source_id not in spans
        for source_id in source_ids
    ):
        raise ValueError("source IDs must refer to the current note")
    if len(source_ids) != len(set(source_ids)):
        raise ValueError("source IDs must be unique")
    if not source_ids:
        return ""
    selected = [spans[source_id] for source_id in source_ids]
    return raw_text[min(span.start for span in selected):max(span.end for span in selected)]
