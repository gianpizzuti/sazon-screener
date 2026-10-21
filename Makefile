PY := .venv/bin/python

.PHONY: install web test chat run web-dev seed samples reset-demo

install:       ## Python package + the web app (the web build needs Node 18+)
	python3 -m venv .venv
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install -e ".[dev]"
	@command -v npm >/dev/null && $(MAKE) web || echo "npm not found: the API works, the web app needs Node 18+ (then run: make web)"

web:           ## build the recruiter web app into web/dist (served by the API)
	cd web && npm ci && npm run build

test:
	$(PY) -m pytest -q

run:           ## API + recruiter web app on http://localhost:8000 (demo clock enabled)
	$(PY) scripts/run.py

web-dev:       ## web app with hot reload on http://localhost:5173 (run `make run` too: it proxies /api)
	cd web && npm run dev

chat:          ## talk to the agent in the terminal
	$(PY) -m screener.channels.cli

seed:          ## fill the database with demo candidates (real models, ~0.10 USD each)
	$(PY) scripts/seed_demo.py

samples:       ## export finished demo conversations to samples/*.md
	$(PY) scripts/export_samples.py

reset-demo:    ## DELETES the local database and demo clock, then re-seeds the demo candidates
	rm -f data/screener.db data/demo_clock.json
	$(PY) scripts/seed_demo.py
