"""Combine all stages into category scores, an overall score, knockout flags
and impact-ranked recommendations.

Category weights mirror how real pipelines behave:
- Parsing failures hurt you everywhere (same few engines under every ATS).
- Keyword match decides whether a recruiter's search ever surfaces you.
- Content quality decides what happens in the recruiter's 7-second skim.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from . import extract as ex_mod
from . import match as match_mod
from . import parse as parse_mod
from . import quality as q_mod


@dataclass
class Check:
    cid: str
    label: str
    score: float          # 0.0 - 1.0
    weight: float         # relative weight inside its category
    message: str
    fix: str = ""

    @property
    def tier(self) -> str:  # good -> bad: green / yellow / orange / red
        if self.score >= 0.8:
            return "green"
        if self.score >= 0.6:
            return "yellow"
        if self.score >= 0.4:
            return "orange"
        return "red"


@dataclass
class Category:
    name: str
    weight: float         # share of the overall score, 0-1
    checks: list = field(default_factory=list)

    @property
    def score(self) -> float:
        total = sum(c.weight for c in self.checks)
        if not total:
            return 0.0
        return round(100 * sum(c.score * c.weight for c in self.checks) / total, 1)


@dataclass
class Report:
    resume_path: str = ""
    jd_path: str = ""
    error: str = ""
    overall: float = 0.0
    grade: str = ""
    grade_note: str = ""
    categories: list = field(default_factory=list)
    knockouts: list = field(default_factory=list)
    recommendations: list = field(default_factory=list)   # (impact, label, fix)
    profile: dict = field(default_factory=dict)           # what the ATS "sees"
    keywords: dict = field(default_factory=dict)


def _scale(value, lo, hi) -> float:
    """0 at lo, 1 at hi, linear in between."""
    if hi == lo:
        return 1.0
    return max(0.0, min(1.0, (value - lo) / (hi - lo)))


# ---------------------------------------------------------------- categories

def _parse_checks(ex, pr) -> list:
    checks = []
    words = ex.words
    checks.append(Check(
        "text", "Readable text layer",
        1.0 if words >= 120 else (0.5 if words >= 40 else 0.0),
        3,
        f"{words} words extracted" + ("" if words >= 120 else " - dangerously little"),
        "" if words >= 120 else "Re-export as a text-based PDF or DOCX; verify by "
        "selecting the text in a viewer."))

    hazard_meta = {
        "tables": ("Tables", 0.2, 2.5), "multi_column": ("Single-column layout", 0.2, 2.5),
        "images": ("No images/graphics", 0.5, 1), "text_boxes": ("No text boxes", 0.2, 2.5),
        "header_footer": ("Contact info in body", 0.4, 1.5),
        "scanned_pdf": ("Not a scanned image", 0.0, 3), "no_text": ("Not empty", 0.0, 3),
    }
    seen = set()
    for hz in ex.hazards:
        label, sc, w = hazard_meta.get(hz.code, (hz.code, 0.4, 1))
        seen.add(hz.code)
        checks.append(Check("hz_" + hz.code, label, 0.0 if hz.severe else sc, w,
                            hz.message, hz.fix))
    for code, (label, _sc, w) in hazard_meta.items():
        if code not in seen and code in ("tables", "multi_column", "images", "text_boxes"):
            checks.append(Check("hz_" + code, label, 1.0, w,
                                "None detected - parses cleanly", ""))

    ft_score = {"pdf": 1.0, "docx": 1.0, "txt": 0.85, "md": 0.7}.get(ex.filetype, 0.0)
    checks.append(Check(
        "filetype", "ATS-friendly file type", ft_score, 1,
        f".{ex.filetype} file",
        "" if ft_score >= 0.85 else "Submit a text-based PDF or DOCX."))

    c = pr.contact
    checks.append(Check(
        "email", "Email found", 1.0 if c.email else 0.0, 2,
        c.email or "No email address detected",
        "" if c.email else "Add a plain-text email near the top (not inside a "
        "header, image or icon)."))
    checks.append(Check(
        "phone", "Phone found", 1.0 if c.phone else 0.0, 1.5,
        c.phone or "No phone number detected",
        "" if c.phone else "Add a phone number near the top in a standard format."))
    checks.append(Check(
        "linkedin", "LinkedIn/portfolio link", 1.0 if (c.linkedin or c.github) else 0.5, 0.5,
        c.linkedin or c.github or "No LinkedIn/GitHub URL found",
        "" if (c.linkedin or c.github) else "Add your LinkedIn URL - most recruiters "
        "look for it."))

    core = ["experience", "education", "skills"]
    found = [s for s in core if pr.sections.get(s)]
    missing = [s for s in core if s not in found]
    msg = "Found: " + (", ".join(found) or "none")
    fix = ""
    if missing:
        msg += " | missing: " + ", ".join(missing)
        fix = "Use standard headers (Experience, Education, Skills)."
        if pr.unknown_headers:
            fix += (" Nonstandard headers found: "
                    + ", ".join(repr(h) for h in pr.unknown_headers[:4])
                    + " - parsers cannot map these to the right fields.")
    checks.append(Check("sections", "Standard sections detected",
                        len(found) / len(core), 2.5, msg, fix))

    if pr.sections.get("experience") or pr.jobs:
        ok = bool(pr.jobs)
        checks.append(Check(
            "dates", "Job dates parseable", 1.0 if ok else 0.0, 2,
            f"{len(pr.jobs)} dated role(s) found" if ok
            else "No date ranges could be parsed from the work history",
            "" if ok else "Format every role's dates like 'Jan 2022 - Present'; "
            "parsers use them to compute your years of experience."))
    return checks


def _quality_checks(ex, pr, q) -> list:
    checks = []
    nb = len(q.bullets)
    checks.append(Check(
        "quantified", "Quantified achievements",
        _scale(q.pct_quantified, 0.05, 0.45), 3,
        f"{q.pct_quantified:.0%} of {nb} bullet(s) contain numbers ($, %, counts)",
        "" if q.pct_quantified >= 0.45 else
        "Add measurable outcomes to bullets: revenue, %, time saved, users, team "
        "size. Aim for numbers in at least half."))
    checks.append(Check(
        "verbs", "Bullets start with action verbs",
        _scale(q.pct_strong_verb, 0.1, 0.7), 2,
        f"{q.pct_strong_verb:.0%} of bullets open with a strong verb",
        "" if q.pct_strong_verb >= 0.7 else
        "Open each bullet with a strong past-tense verb: Led, Built, Reduced, "
        "Launched, Negotiated..."))

    n_weak = len(q.weak_start_hits)
    checks.append(Check(
        "weak", "No weak/passive phrasing",
        1.0 if n_weak == 0 else (0.5 if n_weak <= 2 else 0.15), 2,
        "None found" if n_weak == 0 else
        f"{n_weak} weak opener(s), e.g. \"{q.weak_start_hits[0]}\"",
        "" if n_weak == 0 else
        "Replace 'Responsible for / Worked on / Helped with' with what you "
        "actually did and its result."))

    n_buzz = len(q.buzzword_hits)
    checks.append(Check(
        "buzzwords", "No empty buzzwords",
        1.0 if n_buzz == 0 else (0.55 if n_buzz <= 2 else 0.15), 1,
        "None found" if n_buzz == 0 else "Found: " + ", ".join(q.buzzword_hits[:6]),
        "" if n_buzz == 0 else
        "Delete self-descriptions like these; show the trait with a concrete "
        "achievement instead."))

    checks.append(Check(
        "pronouns", "No first-person pronouns",
        1.0 if q.pronoun_count == 0 else (0.5 if q.pronoun_count <= 2 else 0.2), 1,
        "None found" if q.pronoun_count == 0 else
        f"{q.pronoun_count} use(s) of I/me/my/we/our",
        "" if q.pronoun_count == 0 else
        "Resumes are written in implied first person: 'Led X', not 'I led X'."))

    pages = ex.page_count
    if q.word_count < 240:
        len_score, len_msg = 0.4, f"Only ~{q.word_count} words - reads as thin"
        len_fix = "Flesh out roles with 3-5 achievement bullets each."
    elif q.word_count < 330:
        len_score, len_msg = 0.75, f"~{q.word_count} words - on the shorter side"
        len_fix = ("Fine for early career; if you have more wins, add a bullet "
                   "or two per role.")
    elif pages <= 2:
        len_score, len_msg, len_fix = 1.0, f"~{pages} page(s), {q.word_count} words", ""
    elif pages == 3:
        len_score, len_msg = 0.5, f"~3 pages ({q.word_count} words)"
        len_fix = "Cut to 2 pages unless you are 15+ years in or in academia."
    else:
        len_score, len_msg = 0.2, f"~{pages} pages ({q.word_count} words)"
        len_fix = "Cut aggressively - recruiters skim; 2 pages max for most roles."
    checks.append(Check("length", "Appropriate length", len_score, 2, len_msg, len_fix))

    if q.bullets:
        abw = q.avg_bullet_words
        checks.append(Check(
            "bullet_len", "Concise bullets",
            1.0 if abw <= 26 else (0.6 if abw <= 34 else 0.3), 1,
            f"Average bullet length {abw:.0f} words",
            "" if abw <= 26 else "Trim bullets to one line, two max (under ~25 words)."))

    n_gaps = len(pr.gaps_over_6mo)
    if pr.jobs:
        checks.append(Check(
            "gaps", "No unexplained gaps",
            1.0 if n_gaps == 0 else (0.6 if n_gaps == 1 else 0.3), 1,
            "No gaps over 6 months" if n_gaps == 0 else
            f"{n_gaps} gap(s) over 6 months (longest {max(pr.gaps_over_6mo)} months)",
            "" if n_gaps == 0 else
            "Recruiters filter on gaps. Cover them (freelance, education, "
            "caregiving) or be ready to explain in one line."))
        tenure = pr.avg_tenure_months
        checks.append(Check(
            "tenure", "Healthy average tenure",
            1.0 if tenure >= 18 else (0.6 if tenure >= 10 else 0.3), 1,
            f"Average {tenure:.0f} months per role",
            "" if tenure >= 18 else
            "Sub-1-year average tenure reads as job-hopping; group short "
            "contract gigs under one 'Consulting' entry."))
        checks.append(Check(
            "date_fmt", "Consistent date format",
            1.0 if len(pr.date_styles) <= 1 else 0.6, 0.5,
            "One date style used" if len(pr.date_styles) <= 1 else
            "Mixed date styles: " + ", ".join(sorted(pr.date_styles)),
            "" if len(pr.date_styles) <= 1 else
            "Pick one format ('Jan 2022') and use it everywhere."))
    return checks


def _match_checks(mr) -> list:
    checks = []
    n_req, n_hit = len(mr.required), len(mr.matched_required)
    checks.append(Check(
        "req_skills", "Required skills matched",
        mr.required_rate if n_req else 1.0, 5,
        f"{n_hit}/{n_req} required skills found"
        + (" | missing: " + ", ".join(mr.missing_required[:8]) if mr.missing_required else ""),
        "" if not mr.missing_required else
        "Add the missing skills you genuinely have, using the JD's exact wording "
        "(recruiters search these terms verbatim)."))
    if mr.preferred:
        checks.append(Check(
            "pref_skills", "Nice-to-have skills matched",
            mr.preferred_rate, 2,
            f"{len(mr.matched_preferred)}/{len(mr.preferred)} preferred skills found"
            + (" | missing: " + ", ".join(mr.missing_preferred[:6])
               if mr.missing_preferred else ""),
            "" if not mr.missing_preferred else
            "Nice-to-haves are tiebreakers - add any you actually have."))

    checks.append(Check(
        "title", "Job title alignment",
        _scale(mr.title_overlap, 0.0, 0.75), 2,
        f"{mr.title_overlap:.0%} of the JD title's key words appear in your "
        f"titles/summary (JD: '{mr.jd_title[:50]}')",
        "" if mr.title_overlap >= 0.75 else
        "Mirror the target title in your headline/summary if it honestly "
        "describes you - recruiters filter by current title."))

    matched_total = mr.matched_required + mr.matched_preferred
    if matched_total:
        ctx_rate = len(mr.in_context) / len(matched_total)
        checks.append(Check(
            "context", "Skills shown in real experience",
            _scale(ctx_rate, 0.2, 0.8), 1,
            f"{len(mr.in_context)}/{len(matched_total)} matched skills appear inside "
            "your experience bullets (not just the skills list)",
            "" if ctx_rate >= 0.8 else
            "A bare skills-list mention looks like keyword stuffing; work key "
            "skills into achievement bullets."))
    return checks


def _years_check(mr, pr) -> Check | None:
    if not mr.jd_years:
        return None
    have = max(pr.total_years, float(pr.stated_years))
    if have >= mr.jd_years:
        sc = 1.0
    elif have >= 0.75 * mr.jd_years:
        sc = 0.6
    else:
        sc = 0.2
    return Check(
        "years", "Years of experience", sc, 2,
        f"JD asks for {mr.jd_years}+ years; your dated history shows ~{pr.total_years:g}",
        "" if sc == 1.0 else
        "If you have adjacent experience (internships, freelance), date it "
        "clearly - parsers compute years from your date ranges.")


def _degree_check(mr) -> Check | None:
    if not mr.jd_degree:
        return None
    names = {1: "Associate", 2: "Bachelor's", 3: "Master's", 4: "PhD"}
    ok = mr.resume_degree >= mr.jd_degree
    return Check(
        "degree", "Education requirement", 1.0 if ok else 0.3, 1,
        f"JD asks for {names[mr.jd_degree]}; resume shows "
        + (names.get(mr.resume_degree, "no detectable degree")),
        "" if ok else
        "If you hold the degree, spell it out ('B.S. in X, University, Year') in "
        "an Education section; if not, lead with certifications and experience.")


# ------------------------------------------------------------------- driver

def grade(resume_path, jd_path=None) -> Report:
    rep = Report(resume_path=str(resume_path), jd_path=str(jd_path or ""))
    ex = ex_mod.extract(resume_path)
    if ex.error:
        rep.error = ex.error
        rep.grade, rep.grade_note = "F", "File could not be read at all."
        rep.knockouts.append(ex.error)
        return rep

    pr = parse_mod.parse(ex.text)
    q = q_mod.analyze(ex, pr)

    cats = [Category("Parse & format", 0.55, _parse_checks(ex, pr)),
            Category("Content quality", 0.45, _quality_checks(ex, pr, q))]

    mr = None
    if jd_path:
        jd_text = Path(jd_path).read_text(encoding="utf-8", errors="replace")
        mr = match_mod.compare(jd_text, ex.text, pr)
        mchecks = _match_checks(mr)
        for extra in (_years_check(mr, pr), _degree_check(mr)):
            if extra:
                mchecks.append(extra)
        cats = [Category("Parse & format", 0.35, cats[0].checks),
                Category("Keyword match", 0.40, mchecks),
                Category("Content quality", 0.25, cats[1].checks)]
    rep.categories = cats

    # Knockouts: the things that genuinely get resumes dropped automatically.
    if ex.words < 40:
        rep.knockouts.append("No readable text layer - an ATS imports a blank "
                             "candidate. This alone explains silent rejections.")
    if not pr.contact.email and not pr.contact.phone:
        rep.knockouts.append("No email or phone detected - recruiters cannot "
                             "contact you even if they like the resume.")
    if mr and len(mr.required) >= 4 and mr.required_rate < 0.25:
        rep.knockouts.append(
            f"Only {len(mr.matched_required)}/{len(mr.required)} required skills "
            "matched - a recruiter keyword search would never surface this resume "
            "for this role.")

    rep.overall = round(sum(c.score * c.weight for c in cats), 1)
    rep.grade, rep.grade_note = _letter(rep.overall, bool(rep.knockouts))

    # Impact-ranked recommendations
    recs = []
    for cat in cats:
        cat_total = sum(c.weight for c in cat.checks) or 1
        for c in cat.checks:
            if c.score < 0.8 and c.fix:
                impact = cat.weight * (c.weight / cat_total) * (1 - c.score) * 100
                recs.append((round(impact, 1), c.label, c.fix))
    recs.sort(key=lambda r: -r[0])
    seen_fix = set()
    for r in recs:
        if r[2] not in seen_fix:
            rep.recommendations.append(r)
            seen_fix.add(r[2])
    rep.recommendations = rep.recommendations[:7]

    # What the machine sees
    rep.profile = {
        "name": pr.name_guess or "(not detected)",
        "email": pr.contact.email or "(not detected)",
        "phone": pr.contact.phone or "(not detected)",
        "linkedin": pr.contact.linkedin or pr.contact.github or "(not detected)",
        "sections": sorted(k for k in pr.sections if k != "preamble" and pr.sections[k]),
        "roles_parsed": len(pr.jobs),
        "years_experience": pr.total_years,
        "skills_recognized": match_mod.find_all_skills(ex.text),
        "pages": ex.page_count,
        "words": ex.words,
    }
    if mr:
        rep.keywords = {
            "jd_title": mr.jd_title,
            "matched_required": mr.matched_required,
            "missing_required": mr.missing_required,
            "matched_preferred": mr.matched_preferred,
            "missing_preferred": mr.missing_preferred,
            "keyword_stuffing_risk": mr.only_in_skill_list,
            "other_jd_terms_absent": mr.other_jd_terms,
        }
    return rep


def _letter(score, has_knockouts):
    if has_knockouts:
        return "F", "Knockout condition - likely filtered before a human ever looks."
    if score >= 85:
        return "A", "Survives parsing and keyword screens at nearly any company."
    if score >= 70:
        return "B", "Solid - a few fixes away from top-tier."
    if score >= 55:
        return "C", "Will pass some screens and silently fail others."
    if score >= 40:
        return "D", "High risk of being filtered or skimmed past."
    return "F", "Very likely rejected before a human reads it."


def to_dict(rep: Report) -> dict:
    return {
        "resume": rep.resume_path,
        "job_description": rep.jd_path,
        "error": rep.error,
        "overall_score": rep.overall,
        "grade": rep.grade,
        "grade_note": rep.grade_note,
        "knockouts": rep.knockouts,
        "categories": [{
            "name": c.name, "weight": c.weight, "score": c.score,
            "checks": [{
                "id": ch.cid, "label": ch.label, "score": round(ch.score, 2),
                "tier": ch.tier, "weight": ch.weight,
                "detail": ch.message, "fix": ch.fix,
            } for ch in c.checks],
        } for c in rep.categories],
        "recommendations": [
            {"impact": r[0], "area": r[1], "fix": r[2]} for r in rep.recommendations],
        "ats_profile": rep.profile,
        "keywords": rep.keywords,
    }
