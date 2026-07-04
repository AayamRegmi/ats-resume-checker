"""Command line interface: cvgrader RESUME [--jd JOB.txt] [--html out.html] [--json [PATH]]"""
from __future__ import annotations

import argparse
import sys

from .report import render_terminal, write_html, write_json
from .score import grade


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="cvgrader",
        description="Grade a resume the way ATS parsers + recruiter keyword "
                    "searches + screening heuristics actually do.")
    ap.add_argument("resume", help="resume file (.pdf, .docx, .txt)")
    ap.add_argument("--jd", metavar="FILE",
                    help="job description text file - enables keyword-match scoring "
                         "(strongly recommended: this is what real screens key on)")
    ap.add_argument("--json", nargs="?", const="-", metavar="PATH",
                    help="write JSON report to PATH (or stdout if no path)")
    ap.add_argument("--html", metavar="PATH", help="write a color HTML report to PATH")
    ap.add_argument("--no-color", action="store_true", help="disable ANSI colors")
    args = ap.parse_args(argv)

    try:
        if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    rep = grade(args.resume, args.jd)

    if args.json:
        written = write_json(rep, args.json)
        if written:
            print(f"JSON report written to {written}")
    if args.json != "-":
        print(render_terminal(rep, no_color=args.no_color))
    if args.html:
        print(f"HTML report written to {write_html(rep, args.html)}")

    return 2 if rep.error else (1 if rep.knockouts else 0)


if __name__ == "__main__":
    sys.exit(main())
