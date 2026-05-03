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

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the app:
   ```bash
   uvicorn app.main:app --reload
   ```

## Next milestones

- Add tags/search filters for contacts
- Add follow-up reminders and due dates
- Add a simple React or Streamlit UI
- Add calendar/email import to auto-log interactions
