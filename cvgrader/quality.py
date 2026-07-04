"""Stage 4: recruiter-style content heuristics (the ResumeWorded/Rezi layer).

None of this auto-rejects anyone in a real pipeline, but it is what a recruiter
scans for in their first 7-8 seconds, and what candidate-side graders score.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from .parse import RANGE_RE

_DATA = Path(__file__).parent / "data"

_BULLET_RE = re.compile(r"^\s*[•▪◦·\-\*\+‣»–—o]\s+")
_QUANT_RE = re.compile(r"\d|%|\$|£|€")
_PRONOUN_RE = re.compile(r"\b(i|me|my|mine|we|our)\b", re.I)


@lru_cache(maxsize=1)
def _verbs():
    return json.loads((_DATA / "verbs.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _buzzwords():
    return json.loads((_DATA / "buzzwords.json").read_text(encoding="utf-8"))["buzzwords"]


@dataclass
class QualityMetrics:
    bullets: list = field(default_factory=list)
    pct_quantified: float = 0.0
    pct_strong_verb: float = 0.0
    weak_start_hits: list = field(default_factory=list)
    buzzword_hits: list = field(default_factory=list)
    pronoun_count: int = 0
    avg_bullet_words: float = 0.0
    word_count: int = 0


def analyze(extraction, parsed) -> QualityMetrics:
    q = QualityMetrics()
    text = extraction.text
    q.word_count = extraction.words

    bullets = [_BULLET_RE.sub("", ln).strip()
               for ln in text.splitlines() if _BULLET_RE.match(ln)]
    if len(bullets) < 3:
        # No bullet markers: treat sentence-like lines as bullets - from the
        # experience section if recognized, otherwise the whole document.
        candidates = parsed.sections.get("experience") or text.splitlines()
        for ln in candidates:
            s = ln.strip()
            if (len(s) > 45 and not RANGE_RE.search(s)
                    and s != s.upper() and "@" not in s):
                bullets.append(s)
    q.bullets = bullets

    if bullets:
        strong = set(_verbs()["strong"])
        weak_starts = _verbs()["weak_starts"]
        n_quant = n_strong = 0
        total_words = 0
        for b in bullets:
            total_words += len(b.split())
            if _QUANT_RE.search(b):
                n_quant += 1
            first = re.sub(r"[^a-z]", "", b.split()[0].lower()) if b.split() else ""
            if first in strong:
                n_strong += 1
            bl = b.lower()
            for w in weak_starts:
                if bl.startswith(w):
                    q.weak_start_hits.append(b[:70])
                    break
        q.pct_quantified = n_quant / len(bullets)
        q.pct_strong_verb = n_strong / len(bullets)
        q.avg_bullet_words = total_words / len(bullets)

    lower = text.lower()
    for phrase in _buzzwords():
        if phrase in lower:
            q.buzzword_hits.append(phrase)
    q.pronoun_count = len(_PRONOUN_RE.findall(text))
    return q
