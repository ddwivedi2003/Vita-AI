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
   # Then open .env and set AZURE_OPENAI_KEY
   ```

   Or set environment variables directly:

   ```powershell
   $env:AZURE_OPENAI_KEY = 'your-key'
   $env:AZURE_OPENAI_ENDPOINT = 'https://your-endpoint/'
   ```

4. Run the app:

```bash
streamlit run main.py
```

## Notes
- API keys must not be committed. Use environment variables or a local `.env` loaded by your shell.
- If you don't set `AZURE_OPENAI_KEY`, AI features will show a configuration warning but the UI will still run.
