"""Rendering: colored terminal report, JSON, and a self-contained HTML report.

Colors run good -> bad: green, yellow, orange, red - keyed to each check's
score tier and each category/overall score.
"""
from __future__ import annotations

import json
import os
import sys
from html import escape
from pathlib import Path

from .score import Report, to_dict

_TIER_ANSI = {"green": "\x1b[32m", "yellow": "\x1b[33m",
              "orange": "\x1b[38;5;208m", "red": "\x1b[31m"}
_TIER_TAG = {"green": "PASS", "yellow": "WARN", "orange": "POOR", "red": "FAIL"}
_TIER_HEX = {"green": "#16a34a", "yellow": "#ca8a04",
             "orange": "#ea580c", "red": "#dc2626"}
_BOLD, _DIM, _RESET = "\x1b[1m", "\x1b[2m", "\x1b[0m"


def _score_tier(score_0_100: float) -> str:
    if score_0_100 >= 80:
        return "green"
    if score_0_100 >= 60:
        return "yellow"
    if score_0_100 >= 40:
        return "orange"
    return "red"


def _use_color(force_off: bool) -> bool:
    if force_off or os.environ.get("NO_COLOR"):
        return False
    if not sys.stdout.isatty():
        return False
    if os.name == "nt":
        os.system("")  # enables VT escape processing in legacy consoles
    return True


def render_terminal(rep: Report, no_color: bool = False) -> str:
    color = _use_color(no_color)

    def paint(txt, code):
        return f"{code}{txt}{_RESET}" if color else txt

    def tierc(txt, tier):
        return paint(txt, _TIER_ANSI[tier])

    out = []
    w = 74
    title = Path(rep.resume_path).name
    vs = f"  vs  {Path(rep.jd_path).name}" if rep.jd_path else ""
    out.append("=" * w)
    out.append(paint(f"  RESUME CHECKER  |  {title}{vs}", _BOLD))
    out.append("=" * w)

    if rep.error:
        out.append("")
        out.append(tierc(f"  FATAL: {rep.error}", "red"))
        out.append("")
        return "\n".join(out)

    tier = _score_tier(rep.overall)
    bar = "#" * int(rep.overall / 5) + "-" * (20 - int(rep.overall / 5))
    out.append("")
    out.append("  OVERALL  " + tierc(f"{rep.overall:g}/100  grade {rep.grade}", tier)
               + "   " + tierc(f"[{bar}]", tier))
    out.append(f"  {rep.grade_note}")
    out.append("")
    for cat in rep.categories:
        ct = _score_tier(cat.score)
        cbar = "#" * int(cat.score / 5) + "-" * (20 - int(cat.score / 5))
        out.append(f"  {cat.name:<18} " + tierc(f"{cat.score:>5g}/100", ct)
                   + f"  {tierc('[' + cbar + ']', ct)}  weight {cat.weight:.0%}")

    out.append("")
    if rep.knockouts:
        out.append(tierc("  !! KNOCKOUT RISKS - these get resumes dropped outright:", "red"))
        for k in rep.knockouts:
            out.append(tierc(f"     * {k}", "red"))
    else:
        out.append(tierc("  No knockout risks detected.", "green"))

    for cat in rep.categories:
        out.append("")
        out.append(paint(f"  -- {cat.name} ({cat.score:g}/100) "
                         + "-" * max(1, w - len(cat.name) - 18), _BOLD))
        for c in cat.checks:
            tag = tierc(f"[{_TIER_TAG[c.tier]}]", c.tier)
            out.append(f"  {tag} {c.label:<32} {c.message}")
            if c.fix and c.tier != "green":
                out.append(paint(f"           fix: {c.fix}", _DIM if color else ""))

    if rep.keywords:
        kw = rep.keywords
        out.append("")
        out.append(paint("  -- Keywords vs job description " + "-" * (w - 33), _BOLD))
        if kw["matched_required"]:
            out.append(tierc("  matched required:  ", "green")
                       + ", ".join(kw["matched_required"]))
        if kw["missing_required"]:
            out.append(tierc("  MISSING required:  ", "red")
                       + ", ".join(kw["missing_required"]))
        if kw["matched_preferred"]:
            out.append(tierc("  matched preferred: ", "green")
                       + ", ".join(kw["matched_preferred"]))
        if kw["missing_preferred"]:
            out.append(tierc("  missing preferred: ", "orange")
                       + ", ".join(kw["missing_preferred"]))
        if kw["other_jd_terms_absent"]:
            out.append(f"  {_DIM if color else ''}also frequent in JD, absent in resume: "
                       + ", ".join(kw["other_jd_terms_absent"])
                       + (_RESET if color else ""))

    p = rep.profile
    out.append("")
    out.append(paint("  -- What the ATS sees (parsed profile) " + "-" * (w - 40), _BOLD))
    out.append(f"  name: {p['name']}   email: {p['email']}   phone: {p['phone']}")
    out.append(f"  link: {p['linkedin']}   roles parsed: {p['roles_parsed']}   "
               f"~{p['years_experience']:g} yrs   {p['pages']} page(s), {p['words']} words")
    out.append(f"  sections: {', '.join(p['sections']) or '(none recognized)'}")
    skills = p["skills_recognized"]
    out.append(f"  skills recognized ({len(skills)}): "
               + (", ".join(skills[:18]) + (" ..." if len(skills) > 18 else "")
                  if skills else "(none)"))

    if rep.recommendations:
        out.append("")
        out.append(paint("  -- TOP FIXES, ranked by score impact " + "-" * (w - 39), _BOLD))
        for i, (impact, label, fix) in enumerate(rep.recommendations, 1):
            it = "red" if impact >= 8 else ("orange" if impact >= 4 else "yellow")
            out.append(tierc(f"  {i}. (+{impact:g} pts) {label}", it))
            out.append(f"       {fix}")
    out.append("")
    return "\n".join(out)


def write_json(rep: Report, path: str | None):
    payload = json.dumps(to_dict(rep), indent=2)
    if path and path != "-":
        Path(path).write_text(payload, encoding="utf-8")
        return path
    print(payload)
    return None


def write_html(rep: Report, path: str) -> str:
    d = to_dict(rep)
    tier = _score_tier(rep.overall)

    def chip(txt, hexc):
        return (f'<span style="background:{hexc}18;color:{hexc};border:1px solid '
                f'{hexc}55;border-radius:99px;padding:2px 10px;margin:2px;'
                f'display:inline-block;font-size:13px">{escape(str(txt))}</span>')

    rows = []
    for cat in d["categories"]:
        ct = _TIER_HEX[_score_tier(cat["score"])]
        rows.append(
            f'<h2>{escape(cat["name"])} <span style="color:{ct}">{cat["score"]:g}/100'
            f'</span> <small style="color:#888">weight {cat["weight"]:.0%}</small></h2>'
            f'<div style="background:#eee;border-radius:6px;height:10px;margin:6px 0 14px">'
            f'<div style="width:{cat["score"]}%;background:{ct};height:10px;'
            f'border-radius:6px"></div></div><table>')
        for c in cat["checks"]:
            hx = _TIER_HEX[c["tier"]]
            fix = (f'<div style="color:#666;font-size:13px;margin-top:3px">fix: '
                   f'{escape(c["fix"])}</div>') if c["fix"] and c["tier"] != "green" else ""
            rows.append(
                f'<tr><td style="width:70px;vertical-align:top;padding:7px 8px">'
                f'<b style="color:{hx}">{_TIER_TAG[c["tier"]]}</b></td>'
                f'<td style="vertical-align:top;padding:7px 8px;width:240px">'
                f'{escape(c["label"])}</td>'
                f'<td style="padding:7px 8px;color:#333">{escape(c["detail"])}{fix}</td></tr>')
        rows.append("</table>")

    kw_html = ""
    if d["keywords"]:
        kw = d["keywords"]
        kw_html = "<h2>Keywords vs job description</h2><p>"
        kw_html += "".join(chip(s, _TIER_HEX["green"]) for s in kw["matched_required"])
        kw_html += "".join(chip(s + " (missing)", _TIER_HEX["red"]) for s in kw["missing_required"])
        kw_html += "<br>"
        kw_html += "".join(chip(s, "#0891b2") for s in kw["matched_preferred"])
        kw_html += "".join(chip(s + " (missing)", _TIER_HEX["orange"]) for s in kw["missing_preferred"])
        kw_html += "</p>"

    recs = ""
    if d["recommendations"]:
        recs = "<h2>Top fixes (ranked by score impact)</h2><ol>"
        for r in d["recommendations"]:
            hx = _TIER_HEX["red" if r["impact"] >= 8 else ("orange" if r["impact"] >= 4 else "yellow")]
            recs += (f'<li style="margin:8px 0"><b style="color:{hx}">+{r["impact"]:g} pts '
                     f'- {escape(r["area"])}</b><br>{escape(r["fix"])}</li>')
        recs += "</ol>"

    knock = ""
    if d["knockouts"]:
        knock = ('<div style="border:2px solid #dc2626;background:#dc262611;'
                 'border-radius:10px;padding:12px 16px;margin:16px 0">'
                 '<b style="color:#dc2626">KNOCKOUT RISKS</b><ul>'
                 + "".join(f"<li>{escape(k)}</li>" for k in d["knockouts"])
                 + "</ul></div>")

    prof = d["ats_profile"]
    skills = "".join(chip(s, "#475569") for s in prof["skills_recognized"]) or "(none)"

    html_doc = f"""<!doctype html><html><head><meta charset="utf-8">
<title>Resume Grade: {escape(Path(rep.resume_path).name)}</title>
<style>
 body{{font-family:Segoe UI,system-ui,sans-serif;max-width:880px;margin:32px auto;
      padding:0 20px;color:#1a1a1a;line-height:1.45}}
 table{{border-collapse:collapse;width:100%}} tr{{border-bottom:1px solid #eee}}
 h1{{margin-bottom:4px}} h2{{margin-top:28px}}
 .score{{font-size:56px;font-weight:800;color:{_TIER_HEX[tier]}}}
</style></head><body>
<h1>Resume Checker report</h1>
<p style="color:#666">{escape(Path(rep.resume_path).name)}
{("&nbsp;vs&nbsp;" + escape(Path(rep.jd_path).name)) if rep.jd_path else ""}</p>
<div class="score">{rep.overall:g}<small style="font-size:22px;color:#888">/100
&nbsp;grade {rep.grade}</small></div>
<p><b>{escape(rep.grade_note)}</b></p>
{knock}
{recs}
{kw_html}
{"".join(rows)}
<h2>What the ATS sees</h2>
<p>name: <b>{escape(str(prof['name']))}</b> &nbsp; email: <b>{escape(str(prof['email']))}</b>
&nbsp; phone: <b>{escape(str(prof['phone']))}</b><br>
roles parsed: <b>{prof['roles_parsed']}</b> &nbsp; ~<b>{prof['years_experience']:g}</b> years
&nbsp; <b>{prof['pages']}</b> page(s), <b>{prof['words']}</b> words<br>
sections: {escape(", ".join(prof['sections']) or "(none)")}</p>
<p>{skills}</p>
<p style="color:#999;font-size:12px;margin-top:40px">Generated by cv-grader -
simulates ATS parsing + recruiter keyword search + screening heuristics.</p>
</body></html>"""
    Path(path).write_text(html_doc, encoding="utf-8")
    return path
