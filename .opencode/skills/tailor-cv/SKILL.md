---
name: tailor-cv
description: Tailor a CV to one job posting from an evidence database. Reads the posting and data/experience.yaml, checks hard filters, maps every requirement to a claim, proposes 2-3 positionings, waits for approval, then builds and verifies an A4 PDF. Use when the user provides a job posting (text, URL or file) and wants a tailored CV.
---

# /tailor-cv

Tailor one CV to one posting. **Nothing is built before the user approves.**

**Rule zero: the CV never says anything the evidence database cannot back.**
Vocabulary may come from `data/phrase-bank.yaml`. Facts, numbers, employers and
skills come only from `data/experience.yaml`.

Reply in the language the user writes in. Write the CV in the language of the
posting unless the user says otherwise.

## Files (relative to the repository root)

| File | Use |
|---|---|
| `data/experience.yaml` | Source of truth: claims (`weight`), skills (`level`), `do_not_claim` |
| `data/criteria.yaml` | What a relevant job is: hard filters, target roles, scoring |
| `data/phrase-bank.yaml` | Vocabulary only, never facts |
| `data/cv-content.json` | Current CV as structured data; a reference, not a source of facts |
| `template/cv-template.html` | A4 template. Do not edit unless asked |
| `data/history.json`, `data/gap-log.md` | Written at the end by `scripts/writeback.py` |
| `output/` | One folder per application |

## Workflow

### 1. Read
- Get the posting: pasted text, file path, or URL. If it is thin or truncated,
  say so and ask for the full description.
- Read `data/experience.yaml`, `data/criteria.yaml`, `data/phrase-bank.yaml`.
- Extract: role, seniority, must-haves, nice-to-haves, keywords, language
  requirements, location/remote policy, contract type, salary.
- Apply the hard filters in `criteria.yaml` first. If one fires (on-site only,
  clearance required, blocked language, wrong contract, salary below the floor),
  say so plainly and ask whether to continue before spending effort. Do not
  score a role as "Apply" while a hard filter is failing.

### 2. Map requirements to the database
Build a coverage table: for each requirement, the matching skill level
(`shipped` / `working` / `conceptual` / `none`) and the claim IDs behind it.

- `shipped`, and `working` worded modestly, can be claimed.
- `conceptual` and `none` are **gaps**. Never claim them.
- Skills with `show: on_demand` enter only if the posting asks for them.
- `weight: interview` claims never go on a CV.

### 3. Propose 2-3 positionings
Each positioning has a one-line angle, a headline, a profile summary, the skills
block order, and the experience bullets. For every bullet, show its status and
the claim behind it:

| Status | Meaning |
|---|---|
| kept | same as the claim (cite the id) |
| reworded | same facts, new vocabulary (cite id + phrase-bank theme) |
| dropped | in the database but omitted, and why |
| added | in the database but not in the current CV (cite id) |

Numbers and scope must be identical to the database; only vocabulary and
emphasis may change. List the gaps explicitly (requirement, level, rough cost
to close). Keep the CV to 3 pages and say whether 2 are possible.

### 4. Wait for approval
Stop. Ask the user to choose, correct and approve. Build nothing until they
say yes. If they correct a fact, check it against the database; if the database
is wrong or incomplete, propose the edit and ask before writing it.

### 5. Build
1. Create `output/<YYYY-MM-DD>-<company>-<role>/`.
2. Write `cv-content.json` there, same schema as `data/cv-content.json`
   (inline markup: `**bold**`, `[text](url)`).
3. Write `trace.md`: every bullet and profile sentence with its claim IDs.
4. Build:
   ```bash
   python3 scripts/build_pdf.py --content <folder>/cv-content.json --out <folder>/cv.pdf
   ```
5. Verify:
   ```bash
   python3 scripts/verify_pdf.py --pdf <folder>/cv.pdf --spec <folder>/verify.json
   ```
   `verify.json` lists `must_include` (company, role keywords, contact) and
   `must_exclude` (forbidden terms, `do_not_claim` phrases) plus `max_pages`.
6. Re-read the PDF text and confirm nothing is cut off, links survive, and rule
   zero holds against `trace.md`.
7. Report the PDF path and the final gap list.

### 6. Write-back
Only with the user's confirmation:
- New skills, corrections or claims go into `data/experience.yaml` (keep the
  YAML valid; prefer `note_update`-style edits over duplicates).
- Applications and gaps go through the script:
  ```bash
  python3 scripts/writeback.py --file <folder>/writeback.json
  ```
  ```json
  {
    "company": "...", "role": "...", "url": "...",
    "verdict": "Apply", "score": 80, "outcome": "tailored",
    "gaps": [{"requirement": "...", "level": "none", "cost": "..."}]
  }
  ```
  When the user reports they applied, set `"outcome": "applied"` and re-run;
  an entry with the same URL is updated, not duplicated.

The user applies. Never submit anything for them.
