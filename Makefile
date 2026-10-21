PY := .venv/bin/python

.PHONY: install test chat run api dashboard seed samples reset-demo

install:
	python3 -m venv .venv
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install -e ".[dev]"

test:
	$(PY) -m pytest -q

chat:          ## talk to the agent in the terminal
	$(PY) -m screener.channels.cli

run:           ## API (port 8000) + recruiter dashboard (port 8501)
	$(PY) scripts/run.py

api:
	$(PY) -m uvicorn screener.api.app:app --port 8000

dashboard:
	$(PY) -m streamlit run dashboard/app.py --server.port 8501

seed:          ## fill the database with demo candidates (real models, ~0.10 USD each)
	$(PY) scripts/seed_demo.py

samples:       ## export finished demo conversations to samples/*.md
	$(PY) scripts/export_samples.py

reset-demo:    ## DELETES the local database and demo clock, then re-seeds the demo candidates
	rm -f data/screener.db data/demo_clock.json
	$(PY) scripts/seed_demo.py
