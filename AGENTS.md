# AGENTS.md

This repository turns an evidence database into tailored CVs. If you are an
agent working here, read `.opencode/skills/tailor-cv/SKILL.md` — it is the
canonical workflow. This file only adds the repo's non-negotiables.

## Rule zero

**A CV never says anything the evidence database cannot back.**

- Facts, numbers, employers and dates come only from `data/experience.yaml`.
- `data/phrase-bank.yaml` supplies vocabulary, never facts.
- Skills marked `conceptual` or `none` are gaps, not bullet points.
- Anything listed under `do_not_claim` is forbidden.
- Claims marked `weight: interview` never reach a CV.

If the user asks for something the database cannot support, say so and offer
the database edit instead of a softer sentence.

## Non-negotiables

- Never submit an application, send an email, or contact a recruiter or
  employer. The user applies; you prepare.
- Never commit or push. Leave the working tree for the user to review.
- Never invent a metric, a date, a title or a technology. When in doubt, read
  the claim and quote its wording.
- Personal data stays in `data/` and `output/`, which are git-ignored. Do not
  move it into committed files, tests or examples.

## Layout

| Path | What it is |
|---|---|
| `data/` | The user's real data (ignored by git): experience, criteria, CV content |
| `examples/` | Placeholder data shipped with the repo |
| `template/` | A4 print template, fonts, icons |
| `scripts/` | `init`, `build_pdf`, `verify_pdf`, `writeback` |
| `output/` | One folder per application (ignored by git) |

## Commands

```bash
python3 scripts/build_pdf.py --content <folder>/cv-content.json --out <folder>/cv.pdf
python3 scripts/verify_pdf.py --pdf <folder>/cv.pdf --spec <folder>/verify.json
python3 scripts/writeback.py  --file <folder>/writeback.json
```

Paths are relative to the repository root. `CHROME_PATH` overrides Chrome
auto-detection when several browsers are installed.
