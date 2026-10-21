"""Start the API and the recruiter dashboard together. Ctrl+C stops both."""

import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable

# Local runs enable the demo clock (never in production).
api_env = {**os.environ, "SCREENER_DEMO_TOOLS": os.environ.get("SCREENER_DEMO_TOOLS", "1")}
processes = [
    subprocess.Popen([PY, "-m", "uvicorn", "screener.api.app:app", "--port", "8000"], cwd=ROOT, env=api_env),
    subprocess.Popen([PY, "-m", "streamlit", "run", "dashboard/app.py", "--server.port", "8501"], cwd=ROOT),
]
print("\n  Dashboard → http://localhost:8501\n  API docs  → http://localhost:8000/docs\n  (Ctrl+C to stop)\n", flush=True)
try:
    while all(p.poll() is None for p in processes):
        time.sleep(0.5)
except KeyboardInterrupt:
    pass
finally:
    for p in processes:
        p.terminate()
    for p in processes:
        p.wait(timeout=10)
