.PHONY: public-smoke

PYTHON ?= python3

public-smoke:
	$(PYTHON) demo/results/public_smoke/run_public_smoke_test.py
