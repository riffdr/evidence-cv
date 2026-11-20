.PHONY: init pdf verify log clean help

PYTHON ?= python3
OUT    ?= output/cv.pdf

help:
	@echo "make init    create data/ from examples/ and set your identity"
	@echo "make pdf     build $(OUT) from data/cv-content.json"
	@echo "make verify  check $(OUT) against data/verify.json (needs pypdf)"
	@echo "make log     record an application: make log FILE=output/<folder>/writeback.json"
	@echo "make clean   remove generated PDFs and rendered HTML"

init:
	$(PYTHON) scripts/init.py

pdf:
	$(PYTHON) scripts/build_pdf.py --content data/cv-content.json --out $(OUT)

verify:
	$(PYTHON) scripts/verify_pdf.py --pdf $(OUT) --spec data/verify.json

log:
	@test -n "$(FILE)" || (echo "usage: make log FILE=output/<folder>/writeback.json"; exit 1)
	$(PYTHON) scripts/writeback.py --file $(FILE)

clean:
	find output -type f \( -name '*.pdf' -o -name '*.html' \) -delete 2>/dev/null || true
