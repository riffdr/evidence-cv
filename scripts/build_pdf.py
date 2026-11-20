#!/usr/bin/env python3
"""Render the A4 CV template and a content JSON into a PDF with headless Chrome.

    python3 scripts/build_pdf.py --content data/cv-content.json --out output/cv.pdf

Standard library only. Chrome is located via CHROME_PATH (or GOOGLE_CHROME_PATH),
then PATH, then the usual macOS / Linux / Windows install locations.

Markup allowed inside content strings: **bold** and [text](url).
Assets (fonts, icons) are resolved relative to the template directory, so a
template that lives somewhere else can be passed with --template.
"""
import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/usr/bin/google-chrome",
    "/usr/bin/google-chrome-stable",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    "/snap/bin/chromium",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
]


def find_chrome() -> str:
    for var in ("CHROME_PATH", "GOOGLE_CHROME_PATH"):
        candidate = os.environ.get(var)
        if candidate and Path(candidate).exists():
            return candidate
    for name in ("google-chrome", "google-chrome-stable", "chromium",
                 "chromium-browser", "chrome", "msedge"):
        found = shutil.which(name)
        if found:
            return found
    for candidate in CHROME_CANDIDATES:
        if Path(candidate).exists():
            return candidate
    sys.exit(
        "error: no Chrome/Chromium/Edge binary found.\n"
        "Set CHROME_PATH to the executable, e.g.\n"
        "  export CHROME_PATH='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'"
    )


def inline(text: str) -> str:
    """Escape HTML, then allow **bold** and [text](url)."""
    out = html.escape(text, quote=False)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', out)
    return out


def bullets(items) -> str:
    parts = []
    for item in items:
        if isinstance(item, dict):
            kids = bullets(item.get("children", []))
            parts.append(f"<li>{inline(item['text'])}{kids}</li>")
        else:
            parts.append(f"<li>{inline(item)}</li>")
    return f"<ul>{''.join(parts)}</ul>"


def render_blocks(c: dict) -> dict:
    ct = c["contact"]
    icon = lambda n: f'<img src="{{{{assets}}}}/assets/icons/{n}.png" alt="">'
    contact = (
        f'<li>{icon("phone")}<span>{html.escape(ct["phone"])}</span></li>'
        f'<li>{icon("mail")}<span>{html.escape(ct["email"])}</span></li>'
        f'<li>{icon("pin")}<span>{html.escape(ct["location"])}</span></li>'
        f'<li>{icon("linkedin")}<a href="{html.escape(ct["linkedin_url"])}">{html.escape(ct["linkedin"])}</a></li>'
    )
    skills = "".join(
        f'<p><b>{html.escape(s["label"])}</b>: {inline(s["text"])}</p>' for s in c["skills"]
    )
    references = "".join(
        '<div class="ref">'
        f'<div class="n">{html.escape(r["name"])}</div>'
        f'<div class="t">{html.escape(r["title"])}</div>'
        f'<div>{html.escape(r["company"])}</div>'
        f'<div>{html.escape(r["email"])}</div>'
        f'<div><a href="{html.escape(r["linkedin_url"])}">{html.escape(r["linkedin"])}</a></div>'
        "</div>"
        for r in c.get("references", [])
    )
    experience = "".join(
        f'<div class="job"><h3>{html.escape(j["title"])}</h3>'
        f'<div class="meta">{html.escape(j["meta"])}</div>{bullets(j["bullets"])}</div>'
        for j in c["experience"]
    )
    return {
        "name": html.escape(c["name"]),
        "headline": html.escape(c["headline"]),
        "contact": contact,
        "skills": skills,
        "education": "".join(f"<p>{inline(x)}</p>" for x in c.get("education", [])),
        "languages": (
            '<ul class="plain">' + "".join(f"<li>{inline(x)}</li>" for x in c["languages"]) + "</ul>"
            if c.get("languages")
            else ""
        ),
        "awards": "".join(f"<p>{inline(x)}</p>" for x in c.get("awards", [])),
        "references": references,
        "profile": "".join(f"<p>{inline(x)}</p>" for x in c.get("profile", [])),
        "experience": experience,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--content", default="data/cv-content.json", help="CV content JSON")
    ap.add_argument("--template", default=str(REPO / "template" / "cv-template.html"))
    ap.add_argument("--assets", default=None, help="asset root (default: the template's directory)")
    ap.add_argument("--out", default="output/cv.pdf", help="PDF to write")
    ap.add_argument("--keep-html", action="store_true", help="keep the rendered HTML next to the PDF")
    args = ap.parse_args()

    content_path = Path(args.content).expanduser()
    template_path = Path(args.template).expanduser()
    if not content_path.exists():
        sys.exit(f"error: content not found: {content_path}")
    if not template_path.exists():
        sys.exit(f"error: template not found: {template_path}")

    content = json.loads(content_path.read_text(encoding="utf-8"))
    page = template_path.read_text(encoding="utf-8")
    assets = Path(args.assets).expanduser().resolve() if args.assets else template_path.resolve().parent

    blocks = render_blocks(content)

    # An empty block removes its whole sidebar/main section, heading included,
    # so a CV without awards or references has no empty heading.
    for key, value in blocks.items():
        if value.strip():
            continue
        empty_section = r"<section[^>]*>\s*<h2>[^<]*</h2>\s*\{\{" + key + r"\}\}\s*</section>\s*"
        page = re.sub(empty_section, "", page)

    for key, value in blocks.items():
        page = page.replace("{{" + key + "}}", value)
    page = page.replace("{{assets}}", assets.as_uri())

    out = Path(args.out).expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)
    if args.keep_html:
        html_path = out.with_suffix(".html")
    else:
        fd, tmp = tempfile.mkstemp(suffix=".html")
        os.close(fd)
        html_path = Path(tmp)
    html_path.write_text(page, encoding="utf-8")

    chrome = find_chrome()
    with tempfile.TemporaryDirectory() as profile:
        result = subprocess.run(
            [
                chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                "--allow-file-access-from-files", f"--user-data-dir={profile}",
                f"--print-to-pdf={out}", html_path.as_uri(),
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )

    if not args.keep_html:
        html_path.unlink(missing_ok=True)

    if result.returncode != 0 or not out.exists():
        print(result.stderr or result.stdout, file=sys.stderr)
        return 1

    print(f"OK {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
