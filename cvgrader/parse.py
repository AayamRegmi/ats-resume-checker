"""Stage 2: structure the extracted text the way an ATS does -
contact fields, canonical sections, job entries with date ranges.
"""
from __future__ import annotations

import datetime as _dt
import re
from dataclasses import dataclass, field

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE_RE = re.compile(r"\+?\(?\d[\d\s().\-]{7,16}\d")
LINKEDIN_RE = re.compile(r"linkedin\.com/in/[\w\-%]+", re.I)
GITHUB_RE = re.compile(r"github\.com/[\w\-]+", re.I)

SECTION_ALIASES = {
    "summary": ["summary", "professional summary", "profile", "professional profile",
                "objective", "career objective", "about", "about me"],
    "experience": ["experience", "work experience", "professional experience",
                   "employment", "employment history", "work history", "career history",
                   "relevant experience", "professional background"],
    "education": ["education", "academic background", "academics",
                  "education & training", "education and training"],
    "skills": ["skills", "technical skills", "core competencies", "key skills",
               "skills & tools", "skills and tools", "technologies", "tech stack",
               "areas of expertise", "core skills"],
    "projects": ["projects", "personal projects", "selected projects",
                 "academic projects", "key projects"],
    "certifications": ["certifications", "certificates", "licenses",
                       "licenses & certifications", "licenses and certifications"],
    "awards": ["awards", "honors", "honors & awards", "achievements", "accomplishments"],
    "publications": ["publications", "research"],
    "volunteering": ["volunteering", "volunteer experience", "volunteer work", "community involvement"],
    "languages": ["languages"],
    "interests": ["interests", "hobbies"],
}
_ALIAS_TO_CANON = {a: canon for canon, aliases in SECTION_ALIASES.items() for a in aliases}

_MONTHS = {m: i + 1 for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])}
_MONTH_RE = (r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?"
             r"|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)")
_DATE_RE = rf"(?:{_MONTH_RE}\.?,?\s*\d{{4}}|\d{{1,2}}[/.]\d{{4}}|(?:19|20)\d{{2}})"
RANGE_RE = re.compile(
    rf"({_DATE_RE})\s*(?:-|–|—|to|through|thru)\s*"
    rf"({_DATE_RE}|present|current|now|today|ongoing)",
    re.I)


@dataclass
class Contact:
    email: str = ""
    phone: str = ""
    linkedin: str = ""
    github: str = ""


@dataclass
class Job:
    title_hint: str
    start: tuple  # (year, month)
    end: tuple
    current: bool
    style: str  # 'month-name' | 'numeric' | 'year-only'

    @property
    def months(self) -> int:
        return max(1, _ym(self.end) - _ym(self.start) + 1)


@dataclass
class ParsedResume:
    contact: Contact = field(default_factory=Contact)
    name_guess: str = ""
    sections: dict = field(default_factory=dict)          # canonical -> list[str]
    unknown_headers: list = field(default_factory=list)   # caps lines that look like headers
    jobs: list = field(default_factory=list)
    date_styles: set = field(default_factory=set)
    total_years: float = 0.0
    gaps_over_6mo: list = field(default_factory=list)     # list of gap lengths in months
    avg_tenure_months: float = 0.0
    stated_years: int = 0


def _ym(t) -> int:
    return t[0] * 12 + t[1]


def _now_ym() -> tuple:
    today = _dt.date.today()
    return (today.year, today.month)


def _token_to_ym(tok: str, is_end: bool = False):
    tok = tok.strip().lower().rstrip(".,")
    if tok in ("present", "current", "now", "today", "ongoing"):
        return _now_ym(), "current"
    m = re.match(rf"({_MONTH_RE})\.?,?\s*(\d{{4}})$", tok)
    if m:
        return (int(m.group(2)), _MONTHS[m.group(1)[:3]]), "month-name"
    m = re.match(r"(\d{1,2})[/.](\d{4})$", tok)
    if m and 1 <= int(m.group(1)) <= 12:
        return (int(m.group(2)), int(m.group(1))), "numeric"
    m = re.match(r"((?:19|20)\d{2})$", tok)
    if m:
        y = int(m.group(1))
        return (y, 12 if is_end else 1), "year-only"
    return None, ""


def _norm_header(line: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z&' ]", " ", line.lower())).strip()


def parse(text: str) -> ParsedResume:
    pr = ParsedResume()
    lines = text.splitlines()

    # --- contact ---
    m = EMAIL_RE.search(text)
    if m:
        pr.contact.email = m.group(0).rstrip(".")
    m = LINKEDIN_RE.search(text)
    if m:
        pr.contact.linkedin = m.group(0)
    m = GITHUB_RE.search(text)
    if m:
        pr.contact.github = m.group(0)
    phone_zone = "\n".join(lines[:12] + [ln for ln in lines if re.search(
        r"\b(phone|tel|mobile|cell)\b", ln, re.I)])
    for cand in PHONE_RE.finditer(phone_zone):
        digits = re.sub(r"\D", "", cand.group(0))
        if 9 <= len(digits) <= 15 and not re.fullmatch(r"(19|20)\d{2}(19|20)\d{2}", digits):
            pr.contact.phone = cand.group(0).strip()
            break

    # --- name guess: first short alpha line without contact junk ---
    for ln in lines[:5]:
        s = ln.strip()
        if (s and "@" not in s and not any(ch.isdigit() for ch in s)
                and 1 < len(s.split()) <= 5 and len(s) <= 50
                and s.lower() not in ("resume", "curriculum vitae", "cv")):
            pr.name_guess = s
            break

    # --- sections ---
    current = "preamble"
    pr.sections[current] = []
    for idx, ln in enumerate(lines):
        stripped = ln.strip().rstrip(":")
        norm = _norm_header(stripped)
        if stripped and len(stripped) <= 40 and norm in _ALIAS_TO_CANON:
            current = _ALIAS_TO_CANON[norm]
            pr.sections.setdefault(current, [])
            continue
        if (idx > 1 and stripped and stripped == stripped.upper()
                and 1 <= len(stripped.split()) <= 4 and len(stripped) <= 32
                and re.search(r"[A-Z]{3}", stripped) and norm not in _ALIAS_TO_CANON
                and not RANGE_RE.search(stripped)):
            pr.unknown_headers.append(stripped)
        pr.sections[current].append(ln)

    # --- jobs: prefer the experience section, fall back to the whole document ---
    job_lines = pr.sections.get("experience") or lines
    prev_content = ""
    for ln in job_lines:
        m = RANGE_RE.search(ln)
        if not m:
            if ln.strip():
                prev_content = ln.strip()
            continue
        start, s_style = _token_to_ym(m.group(1))
        end, e_style = _token_to_ym(m.group(2), is_end=True)
        if not start or not end or _ym(start) > _ym(end) or _ym(end) > _ym(_now_ym()) + 12:
            continue
        current_job = e_style == "current"
        for st in (s_style, e_style):
            if st in ("month-name", "numeric", "year-only"):
                pr.date_styles.add(st)
        title = (ln[:m.start()] + ln[m.end():]).strip(" -|,–—\t") or prev_content
        pr.jobs.append(Job(title[:80], start, end, current_job, s_style))

    # --- totals, gaps, tenure ---
    if pr.jobs:
        intervals = sorted((_ym(j.start), _ym(j.end)) for j in pr.jobs)
        merged = [list(intervals[0])]
        for s, e in intervals[1:]:
            if s <= merged[-1][1] + 1:
                merged[-1][1] = max(merged[-1][1], e)
            else:
                merged.append([s, e])
        total_months = sum(e - s + 1 for s, e in merged)
        pr.total_years = round(total_months / 12, 1)
        for (s1, e1), (s2, e2) in zip(merged, merged[1:]):
            gap = s2 - e1 - 1
            if gap > 6:
                pr.gaps_over_6mo.append(gap)
        pr.avg_tenure_months = round(
            sum(j.months for j in pr.jobs) / len(pr.jobs), 1)

    # --- stated years ("7+ years of experience" in summary) ---
    summary_text = " ".join(pr.sections.get("summary", []) + pr.sections.get("preamble", []))
    m = re.search(r"(\d{1,2})\s*\+?\s*years?", summary_text, re.I)
    if m:
        pr.stated_years = int(m.group(1))

    return pr
