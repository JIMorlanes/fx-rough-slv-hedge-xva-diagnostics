.PHONY: public-smoke

PYTHON ?= python3

public-smoke:
	$(PYTHON) demo/run_public_smoke_test.py
