"""Run the API, which also serves the recruiter web app (web/dist) at http://localhost:8000."""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if not (ROOT / "web" / "dist" / "index.html").exists():
    print("The web app is not built yet: run `make web` (needs Node 18+). The API still works at /docs.\n")

# Local runs enable the demo clock (never in production).
env = {**os.environ, "SCREENER_DEMO_TOOLS": os.environ.get("SCREENER_DEMO_TOOLS", "1")}
print("\n  Recruiter app -> http://localhost:8000\n  API docs      -> http://localhost:8000/docs\n  (Ctrl+C to stop)\n", flush=True)
try:
    subprocess.run([sys.executable, "-m", "uvicorn", "screener.api.app:app", "--port", "8000"], cwd=ROOT, env=env, check=False)
except KeyboardInterrupt:
    pass
