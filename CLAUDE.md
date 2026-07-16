# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

EnviroFix is a local, AI-powered environment monitoring and diagnostic platform for Kali Linux. It runs as a background daemon/service that scans the system for broken packages, expired GPG keys, missing kernel headers, library conflicts, and network issues, then uses a locally-running Ollama model (`deepseek-r1:8b`) to explain root causes and generate fix commands. It is Docker-first: the backend runs `apt`/`dpkg`/`dkms` commands directly against the host, so it is only meaningful when actually deployed on a Kali/Debian-based Linux system (or container with those tools mounted in).

## Repository layout

- `backend/` — FastAPI service (Python). Entry point `backend/main.py` imports the app from `backend/api/routes.py`.
- `frontend/` — React + Vite dashboard (dark, Grafana-style UI), built and served via nginx in Docker.
- `frontend-static/` / `simple-frontend/` — static HTML fallback dashboards served directly by nginx without a Node build step.
- `envirofix-daemon.py` — standalone Python script (not containerized) that polls `http://localhost:7070` and fires Linux desktop notifications (`notify-send`) when new issues are detected.
- `envirofix_knowledge/`, `backend/ai/envirofix_knowledge/` — ChromaDB-based RAG store scraped from Kali docs; git-ignored, regenerable, do not hand-edit its contents.
- `backend/envirofix_knowledge/google-cloud-sdk/` — a vendored third-party SDK tree accidentally present under the backend; it is unrelated to the app and should generally be left alone.

## Common commands

Backend (from `backend/`):
```
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 7070 --reload
```

Frontend (from `frontend/`):
```
npm install
npm run dev        # Vite dev server on :3000, expects backend on :7070
npm run build
npm run lint        # eslint.config.js
```

Full stack via Docker Compose (from repo root):
```
docker-compose up -d                       # dev compose: postgres + backend (bind-mounted, --reload) + nginx serving frontend-static
docker-compose -f docker-compose.prod.yml up -d   # prod compose: builds frontend image, healthchecked postgres, named volume for RAG knowledge
```
The backend container talks to Ollama on the **host**, not in a container — `OLLAMA_HOST=http://host.docker.internal:11434` with `extra_hosts: host.docker.internal:host-gateway` in the prod compose file. Ollama must be running on the host with `deepseek-r1:8b` (and `qwen2.5-coder:7b`) pulled.

There is no automated test suite in this repo (`test_ai.py` / `test_notify.py` at the root are ad hoc manual scripts, not pytest suites — run them directly with `python test_ai.py` if needed, not via a test runner).

## Architecture notes

**Two parallel scanning implementations exist — know which one a given entry point uses:**
- `backend/scanners/system_scanner.py` (`full_system_scan`) is the one actually wired into `backend/api/routes.py`, which is what `backend/main.py` serves. It shells out to `apt`/`dpkg` directly and returns a flat `{kernel, broken_dependencies, version_conflicts, upgradable_count, issues}` shape.
- `backend/scanner_engine.py` + the individual `backend/scanners/{apt,gpg,kernel,library,network}_scanner.py` modules (each exposing `scan_apt()`, `scan_gpg()`, etc.) implement an older/alternate per-module scan report, persisted via `backend/db/database.py`'s `ScanResult` table, and consumed by `backend/api/routes_minimal.py` (a separate, simpler FastAPI app — not currently referenced by `main.py`). Don't assume routes.py and routes_minimal.py are equivalent; they expose different response shapes for the same endpoint names (e.g. `/alerts`, `/system`).

**AI analysis layer:** `backend/ai/ai_engine.py` (`analyse_issue`, `warmup_model`) and `backend/ai/enhanced_ai.py` (`analyse_with_context`) both hit the same Ollama endpoint (`http://host.docker.internal:11434/api/generate`, model `deepseek-r1:8b`) with slightly different prompt-building strategies; `routes.py`'s `/analyse` endpoint currently builds its own prompt inline rather than calling either module. When touching AI analysis, check which of these three code paths is actually live before assuming a change takes effect.

**`backend/api/routes.py`'s `/analyse` endpoint respects `USE_OLLAMA`** (env var, default `true`). When `false`, it skips the Ollama call entirely and returns the rule-based fallback (still built from real scan data) — this is what makes the app usable on low-resource hosts without a local LLM.

**RAG/knowledge base:** `backend/ai/scraper.py` scrapes Kali docs into ChromaDB (`backend/ai/envirofix_knowledge/`); `backend/ai/rag_scheduler.py` is meant to refresh it periodically via APScheduler, but the job registration in `scanner_engine.py` (`run_full_scrape` interval job) is currently commented out.

**Database:** SQLAlchemy models in `backend/db/database.py` (`ScanResult`, `Alert`). Defaults to local `sqlite:///./envirofix.db` if `DATABASE_URL` is unset; Docker Compose points it at the `postgres` service instead. `postgres://` URLs are auto-rewritten to `postgresql://` for SQLAlchemy compatibility.

**Frontend:** `frontend/src/App.jsx` is a large single-file dashboard (mostly inline styles; `index.css` also has real `@tailwind` directives and `@layer` component classes — Tailwind is genuinely wired up via `postcss.config.js`/`tailwind.config.js`, not dead config) that polls the backend every 30s and hits `/alerts`, `/system`, `/scan-and-alert`, `/analyse`. `API_BASE` is `import.meta.env.VITE_API_BASE || '/api'` — relative by default, proxied to the backend by nginx (`frontend/nginx.conf`, prod) or Vite's dev proxy (`vite.config.js`, `npm run dev`). `frontend/src/services/api.js` defines an equivalent `EnviroFixAPI` client but `App.jsx` does not currently use it — it has its own inline `apiRequest` helper. `frontend/src/components/` and `frontend/src/context/ScanContext.jsx` contain additional dashboard components not wired into `App.jsx`'s current render path; check whether a component is actually imported before assuming it's live. `frontend/Dockerfile` is a multi-stage build (`npm run build` output served by nginx) — do not change it back to running `npm run dev` in the container.

**Deployment:** `.github/workflows/deploy.yml` runs on a self-hosted GitHub Actions runner and redeploys via `docker compose -f docker-compose.prod.yml up -d --build --remove-orphans` on every push to `master`, with health checks against the backend and frontend afterward. `deploy/server-install.sh` is one-time host bootstrap (Docker install + group setup); the runner itself is installed separately. Container ports are bound to `127.0.0.1` in `docker-compose.prod.yml` — a host-level nginx (outside this repo) reverse-proxies the public domain to `127.0.0.1:3000`.

**Requirements files — three exist, only one matters at runtime:** `backend/requirements.txt` is what `backend/Dockerfile` actually installs (`COPY requirements.txt .` + `pip install -r requirements.txt`) — keep it minimal/unpinned to match its existing style. The root `requirements.txt` and `backend/requirements.docker.txt` are both unused by any current Dockerfile; don't assume either reflects what's actually installed in the container.

**Install scripts:** `install.sh` (remote one-liner install target) and `install_local.sh` are shell scripts for provisioning EnviroFix on a fresh Kali box (Docker, Ollama, model pulls, systemd/daemon setup) — read these before changing deployment behavior, since they encode the expected host prerequisites. These are separate from `deploy/server-install.sh`, which targets the Ubuntu/AWS + self-hosted-runner deployment path instead.
