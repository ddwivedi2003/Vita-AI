# Vita AI

Local Streamlit app for health surveillance.

## Setup

1. Create a Python virtual environment and activate it.

   PowerShell:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and fill in your Azure/OpenAI credentials.

   PowerShell:
   ```powershell
   copy .env.example .env
   # Vita AI

   Vita AI is a lightweight Streamlit application for community-driven health surveillance. It combines user-submitted disease reports, geolocation, weather/biometeorological data and optional Azure/OpenAI-powered intelligence to provide localized risk scoring, visualizations and briefings.

   ## Project Summary

   - Purpose: Provide a simple dashboard for collecting and visualizing disease reports, estimating local risk levels, and offering AI-generated briefings and recommendations.
   - Audience: Public health students, researchers, rapid-prototyping teams, and pilots for civic health monitoring.
   - Stack: Python, Streamlit, Pandas, PyDeck, OpenAI/Azure OpenAI (optional), simple CSV files as the datastore.

   ## Key Features

   - User signup/login (CSV-backed)
   - Submit geolocated disease reports with severity
   - Filterable interactive map (nearby vs global)
   - Time-windowed trend charts and alerts
   - Per-user medical profile and report history
   - Optional AI: Daily briefing, trend analysis, symptom assistant (requires Azure/OpenAI credentials)

   ## How It Works (High Level)

   1. Authentication and profiles are stored in `users.csv` and `user_profiles.csv`.
   2. Users submit reports (lat, lng, disease, severity) which are appended to `disease_reports_v2.csv`.
   3. The app computes distances to the user location and aggregates weights into a simple risk score.
   4. Weather data is fetched from the Open-Meteo API to enrich the briefing.
   5. If API credentials are provided, the app calls Azure/OpenAI for: daily briefings, trend analysis and conversational symptom guidance.

   ## Architecture and Code Organization

   The codebase has been modularized into the `vita_ai` package to separate concerns:

   - `vita_ai/config.py`: environment-driven configuration and constants.
   - `vita_ai/utils.py`: helper functions (distance, weather fetch, lottie loader).
   - `vita_ai/auth.py`: `AuthManager` for user CRUD/login backed by CSV.
   - `vita_ai/data.py`: `DataManager` for reports and profile persistence and filtering.
   - `vita_ai/ai.py`: AI-related wrappers that call Azure/OpenAI (client creation, prompts).
   - `vita_ai/ui.py`: Streamlit UI components and page rendering logic.
   - `main.py`: minimal entrypoint that initializes session state and mounts the UI.

   This structure keeps UI, business logic and external integration decoupled and testable.

   ## Data & Privacy

   - Data is stored locally in CSV files (`users.csv`, `user_profiles.csv`, `disease_reports_v2.csv`).
   - Do not commit secrets (API keys) to the repo. Use environment variables or a secrets manager.
   - Consider productionizing storage (Postgres, S3) and adding authentication/authorization for deployments.

   ## Installation

   1. Create and activate a virtual environment (PowerShell example):

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

   3. Configure environment variables. Copy `.env.example` to `.env` or set variables directly.

   Environment variables used by the app:

   - `AZURE_OPENAI_KEY` — (optional) API key for Azure/OpenAI
   - `AZURE_OPENAI_ENDPOINT` — Azure endpoint (default in `.env.example`)
   - `AZURE_OPENAI_MODEL` — model name (default: `gpt-4o`)
   - `AZURE_OPENAI_API_VERSION` — API version (default: `2024-02-01`)

   If you don't provide `AZURE_OPENAI_KEY`, the AI features remain disabled but the UI runs.

   ## Running

   Start the Streamlit app:

   ```bash
   streamlit run main.py
   ```

   Then open the provided `Local URL` in your browser.

   ## Development Notes

   - To run locally without AI, leave `AZURE_OPENAI_KEY` empty.
   - The app uses CSV files in the repo root for simplicity; back them up before large-scale testing.
   - To add automated tests, create unit tests for `vita_ai/utils.py`, `vita_ai/auth.py` and `vita_ai/data.py`.

   ## File Layout (top-level)

   - `main.py` — Streamlit entrypoint
   - `requirements.txt` — Python dependencies
   - `.env.example` — example env vars
   - `disease_reports_v2.csv`, `users.csv`, `user_profiles.csv` — data files (created on first run)
   - `vita_ai/` — package with modularized code

   ## Extending the Project

   - Swap CSVs for a database and add migrations.
   - Add user roles and permissioning for report moderation.
   - Add batching or rate-limiting for incoming reports.
   - Add scheduled jobs to compute and cache trend analytics.

   ## Contributing

   Contributions welcome. Open an issue describing the feature or bug, then submit a small PR with focused changes. Keep secrets out of commits.

   ## License & Contact

   This project is provided as-is for demonstration and prototyping. Add a license file if you plan to publish or collaborate publicly.

   Maintainer: ddwivedi2003
