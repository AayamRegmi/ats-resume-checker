"""Stage 3: keyword/relevance match against a job description.

This replicates the search-and-rank behaviour recruiters actually use inside
Taleo/iCIMS/Workday (boolean keyword search) and the match-rate scoring of
candidate-side tools like Jobscan. Skills are matched via a curated alias
lexicon, split into required vs nice-to-have based on the JD's own wording.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

_DATA = Path(__file__).parent / "data"

_ROLE_WORDS = {
    "engineer", "developer", "manager", "analyst", "designer", "scientist",
    "architect", "lead", "director", "specialist", "consultant", "coordinator",
    "administrator", "accountant", "marketer", "recruiter", "nurse", "teacher",
    "technician", "representative", "associate", "intern", "officer", "head", "vp"}
_STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "for", "to", "in", "at", "on", "with",
    "we", "you", "our", "your", "is", "are", "be", "as", "by", "will", "have",
    "this", "that", "from", "their", "they", "it", "its", "who", "what", "all",
    "can", "may", "must", "should", "would", "about", "into", "than", "them",
    "team", "work", "working", "experience", "years", "strong", "ability",
    "skills", "knowledge", "including", "required", "preferred", "plus", "etc",
    "role", "position", "job", "candidate", "ideal", "looking", "join", "us",
    "other", "using", "used", "use", "such", "more", "well", "good", "great",
    "company", "business", "environment", "across", "within", "per", "each",
    "based", "help", "make", "build", "building", "new", "not", "but", "if"}

_PREF_LINE_RE = re.compile(
    r"\b(nice[\s-]+to[\s-]+have|preferred|a plus|bonus|desirable|ideally|"
    r"advantageous|not required|would be nice)\b", re.I)
_PREF_HEAD_RE = re.compile(r"\b(nice to have|preferred|bonus|plus(?:es)?)\b", re.I)
_REQ_HEAD_RE = re.compile(
    r"\b(requirements?|qualifications?|must[\s-]?haves?|what you.ll need|"
    r"who you are|responsibilit)", re.I)


@lru_cache(maxsize=1)
def _load_groups():
    raw = json.loads((_DATA / "skills.json").read_text(encoding="utf-8"))
    groups = []
    for g in raw["groups"]:
        pats = [_alias_pattern(a, False) for a in g["aliases"]]
        pats += [_alias_pattern(a, True) for a in g.get("cs_aliases", [])]
        groups.append({"name": g["name"], "patterns": pats})
    return groups


def _alias_pattern(alias: str, case_sensitive: bool):
    esc = re.escape(alias if case_sensitive else alias.lower())
    # let spaces/hyphens in an alias match either (via placeholder so the
    # replacement text is never itself rewritten)
    esc = esc.replace(r"\ ", "\x00").replace(r"\-", "\x00").replace(" ", "\x00")
    esc = esc.replace("\x00", r"[\s\-]+")
    pat = r"(?<![\w+#&])" + esc + r"(?![\w+#&])"
    return re.compile(pat, 0 if case_sensitive else re.I)


def _hit(text: str, group) -> bool:
    return any(p.search(text) for p in group["patterns"])


@dataclass
class MatchResult:
    jd_title: str = ""
    required: list = field(default_factory=list)     # skill names in JD 'required' zones
    preferred: list = field(default_factory=list)
    matched_required: list = field(default_factory=list)
    matched_preferred: list = field(default_factory=list)
    missing_required: list = field(default_factory=list)
    missing_preferred: list = field(default_factory=list)
    in_context: list = field(default_factory=list)   # matched skills used inside experience
    only_in_skill_list: list = field(default_factory=list)
    title_overlap: float = 0.0
    jd_years: int = 0
    jd_degree: int = 0        # 0 none, 1 assoc, 2 bachelor, 3 master, 4 phd
    resume_degree: int = 0
    other_jd_terms: list = field(default_factory=list)

    @property
    def required_rate(self) -> float:
        return len(self.matched_required) / len(self.required) if self.required else 1.0

    @property
    def preferred_rate(self) -> float:
        return len(self.matched_preferred) / len(self.preferred) if self.preferred else 1.0


_DEGREE_LEVELS = [
    (4, re.compile(r"\bph\.?\s?d\b|\bdoctorate\b|\bdoctoral\b", re.I)),
    (3, re.compile(r"\bmaster(?:'?s)?\b|\bm\.?s\.?c?\b|\bmba\b|\bm\.?eng\b|\bm\.?a\.\B|\bmsc\b", re.I)),
    (2, re.compile(r"\bbachelor(?:'?s)?\b|\bb\.?s\.?c?\b|\bb\.?a\.\B|\bb\.?tech\b|\bb\.?eng\b|\bundergraduate degree\b", re.I)),
    (1, re.compile(r"\bassociate(?:'?s)? degree\b|\ba\.?a\.?s\.?\b", re.I)),
]


def _degree_level(text: str) -> int:
    for level, pat in _DEGREE_LEVELS:
        if pat.search(text):
            return level
    return 0


def _title_tokens(line: str) -> set:
    return {t for t in re.findall(r"[a-z+#]+", line.lower())
            if t not in _STOPWORDS and len(t) > 1}


def _guess_jd_title(jd_lines) -> str:
    for ln in jd_lines[:6]:
        s = ln.strip()
        if not s:
            continue
        m = re.match(r"(?:job title|position|role)\s*[:\-]\s*(.+)", s, re.I)
        if m:
            return m.group(1).strip()
        if len(s.split()) <= 9 and any(w in s.lower() for w in _ROLE_WORDS):
            return s
    return next((ln.strip() for ln in jd_lines if ln.strip()), "")


def compare(jd_text: str, resume_text: str, parsed) -> MatchResult:
    groups = _load_groups()
    jd_lines = jd_text.splitlines()
    res = MatchResult()
    res.jd_title = _guess_jd_title(jd_lines)

    # Walk the JD, tracking whether we are under a "nice to have" heading.
    zone = "required"
    line_zones = []
    for ln in jd_lines:
        s = ln.strip()
        if s and len(s) <= 60:
            if _PREF_HEAD_RE.search(s) and len(s.split()) <= 6:
                zone = "preferred"
            elif _REQ_HEAD_RE.search(s) and len(s.split()) <= 8:
                zone = "required"
        line_zones.append("preferred" if (_PREF_LINE_RE.search(ln) or zone == "preferred")
                          else "required")

    for g in groups:
        for ln, lz in zip(jd_lines, line_zones):
            if _hit(ln, g):
                (res.preferred if lz == "preferred" else res.required).append(g["name"])
                break

    exp_text = "\n".join(parsed.sections.get("experience", [])
                         + parsed.sections.get("projects", [])
                         + parsed.sections.get("summary", []))
    name_to_group = {g["name"]: g for g in groups}
    for bucket, matched, missing in (
            (res.required, res.matched_required, res.missing_required),
            (res.preferred, res.matched_preferred, res.missing_preferred)):
        for name in bucket:
            g = name_to_group[name]
            if _hit(resume_text, g):
                matched.append(name)
                if _hit(exp_text, g):
                    res.in_context.append(name)
                else:
                    res.only_in_skill_list.append(name)
            else:
                missing.append(name)

    # Title alignment
    jd_tok = _title_tokens(res.jd_title)
    if jd_tok:
        resume_title_text = " ".join(
            [j.title_hint for j in parsed.jobs]
            + parsed.sections.get("summary", [])
            + parsed.sections.get("preamble", [])[:6])
        rt = _title_tokens(resume_title_text)
        res.title_overlap = len(jd_tok & rt) / len(jd_tok)

    # Years of experience asked for
    years = [int(m.group(1)) for m in re.finditer(
        r"(\d{1,2})\s*\+?\s*(?:years?|yrs?)", jd_text, re.I)]
    years = [y for y in years if y <= 15]
    if years:
        res.jd_years = max(years)

    # Degree requirement
    res.jd_degree = _degree_level(jd_text)
    edu_text = " ".join(parsed.sections.get("education", [])) or resume_text
    res.resume_degree = _degree_level(edu_text)

    # Frequent JD terms outside the lexicon that the resume never mentions (info only)
    matched_names = set(res.matched_required + res.matched_preferred
                        + res.missing_required + res.missing_preferred)
    matched_lower = " ".join(matched_names).lower()
    counts: dict[str, int] = {}
    for w in re.findall(r"[a-zA-Z][a-zA-Z+#\-]{3,}", jd_text):
        lw = w.lower()
        if lw not in _STOPWORDS and lw not in matched_lower:
            counts[lw] = counts.get(lw, 0) + 1
    resume_lower = resume_text.lower()
    res.other_jd_terms = sorted(
        (w for w, c in counts.items() if c >= 3 and w not in resume_lower),
        key=lambda w: -counts[w])[:8]
    return res


def find_all_skills(resume_text: str) -> list:
    """Every lexicon skill present in the resume (for the 'what the ATS sees' view)."""
    return [g["name"] for g in _load_groups() if _hit(resume_text, g)]
