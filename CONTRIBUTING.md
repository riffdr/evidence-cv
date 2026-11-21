# Contributing

Thanks for looking. This repo is small on purpose: a data schema, a print
template, and four standard-library scripts. Most useful contributions are
small too.

## What belongs here

Good:

- Fixes to `scripts/` — portability, Chrome detection, error messages, edge cases.
- Template work: print CSS, page breaks, typography, a variant layout.
- `verify_pdf.py` checks that catch real failure modes.
- Documentation, the sample data, or a worked example that shows the workflow end to end.
- Schema proposals, if you have a use case the current one cannot express.

Not here:

- **Real personal data.** Never open a PR containing your CV, your employers,
  your contact details, your history or your gap log. `data/` and `output/` are
  git-ignored for a reason; keep it that way.
- Claims, metrics or technologies added to `examples/` that look like a real
  person's history. The example persona is fictional and stays fictional.
- Dependencies in `build_pdf.py`, `writeback.py` or `init.py`. They are
  standard-library only, and that is the feature.
- Anything that weakens rule zero: a template or script that lets a CV say
  something the evidence database cannot back.

## Ground rules

| Area | Rule |
|---|---|
| Python | 3.10+, standard library only. `verify_pdf.py` may use `pypdf`, but must fail gracefully when it is absent. |
| Shell | Everything runs from the repository root; no absolute paths, no `cd`, no reliance on the current directory. |
| Template | `template/cv-template.html` must stay usable with the shipped example data and produce a PDF with no blank pages. |
| Schema | Claim `id`s and skill keys are referenced by content files: do not rename them silently. Additive changes are preferred; a breaking change needs a note in the PR and a migration line in the README. |
| Privacy | Examples use the fictional persona only. No real names, emails, employers or client names. |

## Before you open a PR

Run the example pipeline from a clean state and confirm all four steps:

```bash
python3 scripts/init.py --force            # rebuild data/ from examples/
python3 scripts/build_pdf.py --content data/cv-content.json --out output/cv.pdf
python3 -m pip install pypdf               # verification only
python3 scripts/verify_pdf.py --pdf output/cv.pdf --spec data/verify.json
python3 scripts/writeback.py --file <(echo '{"company":"Test","role":"Test","url":"","verdict":"Apply","score":1}')
```

Expected: one clean PDF from the example data, `PASS` from verification, and a
history entry that updates rather than duplicates when re-run.

Also check:

- the PDF opens with **no blank pages** and no section heading without content;
- both scripts still run when `CHROME_PATH` is unset on your platform;
- `git status` shows no `data/` or `output/` files.

## Pull requests

- One concern per PR. A CSS fix and a schema change in the same branch is two
  PRs.
- Say what breaks without the change. "Chrome was not found on Fedora" beats
  "improve detection".
- For schema or scoring changes, open an issue first: those affect everyone's
  data and deserve a conversation before code.
- Keep the diff readable: no reformatting of untouched files.

## Commits

Imperative mood, one line, no trailing period:

```
add compact template variant
fix blank page when the last section has no content
verify: fail on blank pages
```

If a commit changes the schema or the scoring model, say so in the body and
explain what existing users should do.

## Licence

By contributing you agree that code and documentation are licensed under the
MIT licence in `LICENSE`. The bundled fonts remain under the SIL Open Font
License 1.1 (`template/fonts/OFL.txt`) and must not be relicensed.

## Conduct

Be decent. Critique the change, not the person. Assume good faith, and remember
that the person on the other side is describing their own career evidence —
treat their data with the care you would want for yours.
