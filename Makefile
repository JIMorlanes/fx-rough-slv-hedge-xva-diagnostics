.PHONY: public-smoke test

PYTHON ?= python3

public-smoke:
	$(PYTHON) demo/run_public_smoke_test.py

test:
	$(PYTHON) -m pytest tests
