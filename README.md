# Personal Network Tracker

A starter personal relationship database for contacts, interactions, and follow-up tracking.

## What this is

- A private app for your own contact records and interaction history.
- Not a social network or public profile service.
- Focused on building the same data modeling, backend, and API skills as your other projects.

## Features included

- Add and list contacts
- Add interaction logs for contacts
- Query contact history and interaction details
- SQLite-backed data storage for quick local use

## Getting started

### Run the app

If dependencies are already installed, start everything with one command:

```bash
./scripts/run_app.sh
```

On macOS, you can also double-click `start_network_tracker.command`.

The launcher starts the FastAPI backend on `http://127.0.0.1:8000` and the Streamlit UI on `http://127.0.0.1:8501`. It uses `.venv/bin/python` directly, so you do not need to activate the virtual environment.

### First-time setup

1. Create the virtual environment:
   ```bash
   python3 -m venv .venv
   ```
2. Install dependencies:
   ```bash
   .venv/bin/pip install -r requirements.txt
   ```
3. Start the app:
   ```bash
   ./scripts/run_app.sh
   ```

## API-only mode

```bash
.venv/bin/python -m uvicorn app.main:app --reload
```

## Next milestones

- Add tags/search filters for contacts
- Add follow-up reminders and due dates
- Add a simple React or Streamlit UI
- Add calendar/email import to auto-log interactions
