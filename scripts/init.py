#!/usr/bin/env python3
"""Create data/ from the shipped examples and fill in your identity.

    python3 scripts/init.py --name "Your Name" --email you@example.com \
        --phone "+34 600 000 000" --location "City, Country" \
        --linkedin "linkedin.com/in/you"

Without flags, any missing field is prompted for (when run in a terminal) or
left at the example placeholder. Existing files are never overwritten unless
--force is passed, so it is safe to re-run.
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
EXAMPLES = REPO / "examples"

PLACEHOLDERS = {
    "name": "Alex Rivera",
    "email": "alex@example.com",
    "phone": "+00 000 000 000",
    "location": "City, Country",
    "linkedin": "linkedin.com/in/example",
}

# Identity lives in these two files; the rest is copied verbatim.
IDENTITY_FILES = ("experience.yaml", "cv-content.json")


def ask(label: str, default: str) -> str:
    if not sys.stdin.isatty():
        return default
    answer = input(f"{label} [{default}]: ").strip()
    return answer or default


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--name")
    ap.add_argument("--email")
    ap.add_argument("--phone")
    ap.add_argument("--location")
    ap.add_argument("--linkedin", help="handle or URL, e.g. linkedin.com/in/you")
    ap.add_argument("--force", action="store_true", help="overwrite existing data/ files")
    args = ap.parse_args()

    data_dir = REPO / "data"
    data_dir.mkdir(exist_ok=True)

    values = {
        "name": args.name or ask("Full name", PLACEHOLDERS["name"]),
        "email": args.email or ask("Email", PLACEHOLDERS["email"]),
        "phone": args.phone or ask("Phone", PLACEHOLDERS["phone"]),
        "location": args.location or ask("Location", PLACEHOLDERS["location"]),
        "linkedin": args.linkedin or ask("LinkedIn", PLACEHOLDERS["linkedin"]),
    }

    copied, skipped = [], []
    for source in sorted(EXAMPLES.iterdir()):
        if not source.is_file():
            continue
        target = data_dir / source.name
        if target.exists() and not args.force:
            skipped.append(source.name)
            continue
        shutil.copyfile(source, target)
        copied.append(source.name)

    for name in IDENTITY_FILES:
        path = data_dir / name
        if not path.exists():
            continue
        # Only rewrite files we just created, unless --force says otherwise.
        if name in skipped:
            continue
        text = path.read_text(encoding="utf-8")
        for key, placeholder in PLACEHOLDERS.items():
            text = text.replace(placeholder, values[key])
        path.write_text(text, encoding="utf-8")

    # A verification spec that always checks the new identity.
    verify_path = data_dir / "verify.json"
    if not verify_path.exists() or args.force:
        verify_path.write_text(
            json.dumps(
                {
                    "must_include": [values["name"], values["email"]],
                    "must_exclude": [],
                    "max_pages": 3,
                    "min_pages": 1,
                },
                indent=2,
                ensure_ascii=False,
            ) + "\n",
            encoding="utf-8",
        )

    print(f"data/ ready at {data_dir}")
    if copied:
        print("  copied:  " + ", ".join(copied))
    if skipped:
        print("  kept:    " + ", ".join(skipped) + "  (use --force to overwrite)")
    print()
    print("Next:")
    print("  1. Replace the example claims in data/experience.yaml with your own.")
    print("  2. Edit data/criteria.yaml: what makes a job worth applying to.")
    print("  3. python3 scripts/build_pdf.py --content data/cv-content.json --out output/cv.pdf")
    return 0


if __name__ == "__main__":
    sys.exit(main())
