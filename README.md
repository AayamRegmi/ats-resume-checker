# cv-grader

Grade your resume the way real hiring pipelines actually do — **before** you apply.

`cv-grader` simulates the three screens a resume passes through at almost every company:

| Stage | What real systems do | What this tool checks |
|---|---|---|
| **1. Parse** | Nearly every ATS (Workday, Greenhouse, iCIMS, Taleo, Lever…) runs your file through one of the same few parsing engines (Textkernel, Sovren, Daxtra). If parsing fails, you're a blank candidate. | Text layer, tables, multi-column layouts, images, text boxes, header/footer traps, contact extraction, standard sections, parseable dates |
| **2. Keyword search** | Recruiters search/filter candidates by the job description's exact terms; tools like Jobscan score the same match rate. | Required vs nice-to-have skill match (155+ skill alias groups), job-title alignment, years of experience, degree requirement, keyword-stuffing detection |
| **3. Human skim** | A recruiter gives the survivors ~7 seconds each. | Quantified achievements, action verbs, weak/passive phrasing, buzzwords, pronouns, length, gaps, tenure, date consistency |

You get **per-category scores, an overall 0–100 score with a letter grade, color-coded findings (green → yellow → orange → red), knockout-risk flags, and fixes ranked by score impact.**

## Install

Requires Python 3.9+.

```bash
pip install git+https://github.com/AayamRegmi/cv-grader.git
```

or with [pipx](https://pipx.pypa.io) (isolated, recommended):

```bash
pipx install git+https://github.com/AayamRegmi/cv-grader.git
```

## Usage

```bash
# Grade against a specific job description (recommended - this is what real screens key on)
cvgrader resume.pdf --jd job_description.txt

# Grade the resume alone (parse + content quality only)
cvgrader resume.pdf

# Extra outputs
cvgrader resume.pdf --jd jd.txt --html report.html   # shareable color report
cvgrader resume.pdf --jd jd.txt --json report.json   # machine-readable
```

Accepts `.pdf`, `.docx` and `.txt`. Save the job posting's text into a `.txt` file for `--jd`.

Try the included samples:

```bash
cvgrader samples/strong_resume.txt --jd samples/sample_jd.txt   # scores ~96 (A)
cvgrader samples/weak_resume.txt   --jd samples/sample_jd.txt   # scores ~43 (F) with knockout flags
```

Exit codes: `0` fine, `1` knockout risk detected, `2` file unreadable — handy in scripts.

## What the output looks like

```
  OVERALL  96.2/100  grade A   [###################-]
  Parse & format      99.3/100  weight 35%
  Keyword match       93.3/100  weight 40%
  Content quality     96.6/100  weight 25%

  [PASS] Required skills matched   12/13 found | missing: Jenkins
  [FAIL] Standard sections         Found: none | missing: experience, education, skills
           fix: Use standard headers (Experience, Education, Skills)...

  -- TOP FIXES, ranked by score impact --
  1. (+16.7 pts) Required skills matched
       Add the missing skills you genuinely have, using the JD's exact wording...
```

Every finding is tiered **green / yellow / orange / red** by severity, and the "What the ATS sees" section shows exactly the profile a parser would import — name, contact, sections, roles, computed years, recognized skills.

## Scoring model

- **With a JD:** Parse & format 35% · Keyword match 40% · Content quality 25%
- **Without a JD:** Parse & format 55% · Content quality 45%
- **Knockouts** (no readable text, no contact info, <25% required-skill match) cap the grade at **F** regardless of points, because that's how they behave in real life.

Note: like the commercial scanners, alternatives in a JD line ("GitHub Actions, Jenkins **or similar**") each count as separate keywords — missing one of an either/or pair costs a little. Real recruiters search this way too.

## Disclaimer

This is a faithful *simulation* of common ATS parsing + screening behavior, not any vendor's actual code. Use it to de-risk your resume; it can't guarantee outcomes. And never add skills you don't have — the goal is to stop good candidates from being filtered out by formatting, not to game your way past the interview.

## License

MIT
