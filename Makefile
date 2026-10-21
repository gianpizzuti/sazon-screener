PY := .venv/bin/python

.PHONY: install test chat

install:
	python3 -m venv .venv
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install -e ".[dev]"

test:
	$(PY) -m pytest -q

chat:
	$(PY) -m screener.channels.cli
