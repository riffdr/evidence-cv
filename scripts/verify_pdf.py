#!/usr/bin/env python3
"""Check a built PDF: required text present, forbidden text absent, page count.

    python3 scripts/verify_pdf.py --pdf output/cv.pdf --spec output/verify.json

verify.json:
  {
    "must_include": ["Acme", "TypeScript", "you@example.com"],
    "must_exclude": ["Karma", "PhD", "secret-project"],
    "max_pages": 3,
    "min_pages": 1,
    "case_sensitive": false
  }

Matching collapses whitespace on both sides, so a phrase broken across a line
wrap ("REST\\nAPIs") still matches. Requires pypdf:

    python3 -m pip install pypdf

Exit codes: 0 all checks pass, 1 a check failed, 2 pypdf missing or bad input.
"""
import argparse
import json
import re
import sys
from pathlib import Path


def squeeze(text: str, case_sensitive: bool) -> str:
    text = re.sub(r"\s+", " ", text)
    return text if case_sensitive else text.lower()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--spec", help="JSON spec file")
    ap.add_argument("--include", action="append", default=[], help="text that must appear (repeatable)")
    ap.add_argument("--exclude", action="append", default=[], help="text that must not appear (repeatable)")
    ap.add_argument("--max-pages", type=int)
    ap.add_argument("--min-pages", type=int)
    ap.add_argument("--case-sensitive", action="store_true")
    args = ap.parse_args()

    spec = {}
    if args.spec:
        spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))

    include = list(spec.get("must_include", [])) + args.include
    exclude = list(spec.get("must_exclude", [])) + args.exclude
    max_pages = args.max_pages or spec.get("max_pages")
    min_pages = args.min_pages or spec.get("min_pages")
    case_sensitive = args.case_sensitive or bool(spec.get("case_sensitive", False))

    pdf_path = Path(args.pdf).expanduser()
    if not pdf_path.exists():
        print(f"error: no such PDF: {pdf_path}", file=sys.stderr)
        return 2

    try:
        from pypdf import PdfReader
    except ImportError:
        print("error: pypdf is required for verification: python3 -m pip install pypdf", file=sys.stderr)
        return 2

    reader = PdfReader(str(pdf_path))
    pages = [page.extract_text() or "" for page in reader.pages]
    text = squeeze("\n".join(pages), case_sensitive)

    failures = []
    if max_pages and len(pages) > max_pages:
        failures.append(f"pages: {len(pages)} > max {max_pages}")
    if min_pages and len(pages) < min_pages:
        failures.append(f"pages: {len(pages)} < min {min_pages}")

    for needle in include:
        if squeeze(needle, case_sensitive) not in text:
            failures.append(f"missing: {needle!r}")

    empties = [i + 1 for i, page in enumerate(pages) if not page.strip()]
    if empties:
        failures.append(f"blank page(s): {empties}")

    for needle in exclude:
        if squeeze(needle, case_sensitive) in text:
            failures.append(f"forbidden: {needle!r}")

    print(f"pages: {len(pages)} | checks: {len(include)} present, {len(exclude)} forbidden")
    if failures:
        for line in failures:
            print(f"FAIL {line}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
