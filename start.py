"""Run the dashboard on http://127.0.0.1:8765 (the address src/tailor.py and src/review_ats.py print).

    python3 start.py

Two processes: FastAPI (dashboard/app.py, reloads on change) serves the API and the built Vue app, and
Vite rebuilds dashboard/web/dist on every change to the front (refresh the page to see it).
Ctrl+C stops both. Read only: data/resume.db is opened with mode=ro.
"""

import signal
import subprocess
import sys
from pathlib import Path

for sig in (signal.SIGTERM, signal.SIGHUP):  # closing the terminal or kill also stops both servers
    signal.signal(sig, lambda *_: sys.exit(0))

ROOT = Path(__file__).resolve().parent
WEB = ROOT / "dashboard" / "web"
PYTHON = ROOT / ".venv" / "bin" / "python"

if not (WEB / "node_modules").exists():
    subprocess.run(["pnpm", "install"], cwd=WEB, check=True)
subprocess.run(["pnpm", "build"], cwd=WEB, check=True)  # so the first page load already has a front

# ponytail: one port, no Vite dev server; switch to `pnpm dev` + a proxy if hot reload is ever missed
front = subprocess.Popen(["pnpm", "build", "--watch"], cwd=WEB, stdout=subprocess.DEVNULL)
back = subprocess.Popen([str(PYTHON), "-m", "uvicorn", "dashboard.app:app", "--host", "127.0.0.1", "--port", "8765",
                         "--reload", "--reload-dir", "dashboard"], cwd=ROOT)
print("Dashboard: http://127.0.0.1:8765")
try:
    sys.exit(back.wait() or front.wait())
except KeyboardInterrupt:
    pass
finally:
    for p in (front, back):
        p.terminate()
        p.wait()
