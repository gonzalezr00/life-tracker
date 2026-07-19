# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Life Tracker** is a personal life-management application: a modular, domain-driven tool for ingesting, storing, and querying personal data across life domains (currently finance and fitness). It exposes both a CLI and a Streamlit UI over a shared core library, backed by a local DuckDB database.

Project root: `/Users/claraferrerrodriguez/dev/life-tracker` (mounted at `/workspaces/life-tracker` inside the dev container).

## Tech Stack
- **Language**: Python 3.11
- **Package manager**: UV (`uv pip`) — see `requirements/base.txt`
- **Storage**: DuckDB (`data/lifetracker.duckdb`)
- **UI**: Streamlit (`app/streamlit_app.py`)
- **CLI**: InquirerPy-based quick-log (`cli/entry.py`)
- **Environment**: Docker dev container (`.devcontainer/`, `Dockerfile`)
- **Notebooks**: Jupyter (carried over from previous ML setup — used for ad-hoc analysis under `workspace/notebooks/`)

## Architecture

The project follows a **core / domains / entrypoints** layout. Domain logic lives in `core/domains/<domain>/` and shares the infrastructure in `core/`.

```
cli/entry.py                  # CLI entry point (InquirerPy quick-log)
app/streamlit_app.py          # Streamlit UI entry point
core/
  models.py                   # Dataclasses: Account, Snapshot
  storage/
    base.py                   # Abstract Repository interface
    duckdb_repo.py            # DuckDB-backed Repository implementation
  domains/
    finance/
      service.py              # Valuation, aggregation, net-worth calculation
      ingestion.py            # Manual entry + market-data ingestion
    fitness/
      test.py                 # Fitness-domain placeholder
data/lifetracker.duckdb       # Local DuckDB database (gitignored)
config.yaml                   # Runtime config (points at personal_info.yaml)
personal_info.yaml            # Sample personal data (income, accounts, assets, liabilities, goals)
session-end.sh                # End-of-session cleanup (commit + Docker cleanup)
workspace/notebooks/          # Ad-hoc Jupyter notebooks
requirements/base.txt         # Python dependencies
```

### Dependency direction

`cli/` and `app/` depend on `core/`. `core/domains/*` depend on `core/storage/` and `core/models.py`. Nothing in `core/` depends on `cli/` or `app/`.

### Adding a new domain

1. Create `core/domains/<domain>/service.py` (business logic) and `core/domains/<domain>/ingestion.py` (data ingestion).
2. Reuse the `Repository` interface in `core/storage/base.py` — prefer the DuckDB implementation unless there's a reason otherwise.
3. Add a new dataclass to `core/models.py` if existing models don't fit.
4. Wire it into both `cli/entry.py` (for terminal use) and `app/streamlit_app.py` (for UI).

## Development Setup

### Option A — Dev container (recommended)
Open the folder in VS Code with the Dev Containers extension. The container is defined by `.devcontainer/devcontainer.json` + `Dockerfile`. The `workspace/` dir is bind-mounted into `/home/dev/project/workspace`.

### Option B — Plain Docker
```bash
docker build -t life-tracker .
docker run -p 8501:8501 -p 8888:8888 \
  -v $(pwd):/home/dev/project \
  life-tracker
```

### Option C — Local (no Docker)
Requires Python 3.11 + UV. From the repo root:
```bash
uv pip install -r requirements/base.txt
```

## Common Commands

- **Run the Streamlit UI**: `streamlit run app/streamlit_app.py` (default port 8501)
- **Run the CLI**: `python cli/entry.py`
- **Start Jupyter** (for ad-hoc analysis): `jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root` → http://localhost:8888
- **Execute a notebook**: `jupyter nbconvert --to notebook --execute <notebook.ipynb> --output <output.ipynb>`
- **Install an extra package**: `uv pip install <package-name>`
- **End-of-session cleanup**: `bash ./session-end.sh` — interactive: prompts to commit/push and offers Docker cleanup options (stop container, remove image, or full prune).

## File Layout Notes

- `data/lifetracker.duckdb` is the local database file and should be gitignored.
- `personal_info.yaml` currently holds **example data for "John Doe"** — treat it as a fixture/sample, not the developer's real information.
- `workspace/notebooks/` is for ad-hoc exploration; outputs go to `workspace/outputs/` to keep notebook dirs clean.
- `.gitignore` is currently empty — it should list `data/lifetracker.duckdb`, `__pycache__/`, `.venv/`, etc.

## State of the Code

Several files are **stubs** (single-line comments only — no implementation yet): `cli/entry.py`, `app/streamlit_app.py`, `core/models.py`, `core/storage/base.py`, `core/storage/duckdb_repo.py`, `core/domains/fitness/test.py`. The finance domain files (`core/domains/finance/service.py`, `core/domains/finance/ingestion.py`) are also stub comments. When implementing, start with `core/storage/base.py` (the Repository contract) and `core/models.py` (Account/Snapshot), then the finance domain, then the CLI/UI entries.

## Best Practices
- Keep domain logic inside `core/domains/<domain>/` — don't bleed it into `cli/` or `app/`.
- Route all storage access through the `Repository` interface; don't import the DuckDB repo directly from domain code.
- Store generated notebook outputs in `workspace/outputs/` rather than next to the notebook.
- Use relative paths in notebooks so they run regardless of where the repo is mounted.
- Commit notebook outputs selectively.
- Run `bash ./session-end.sh` at the end of a working session to commit and clean up Docker artifacts.
