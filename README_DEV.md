# Quick Dev Start — Reserve Flow AI

This short guide helps you run the backend and frontend locally for development or demos using the mock database and a pure-Python JWT strategy.

Backend (quick demo)

1. Create and activate a Python virtual environment:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip setuptools wheel
   ```
2. Install minimal backend dependencies (avoid heavy native libs for quick demos):
   ```powershell
   pip install fastapi uvicorn python-dotenv pydantic pydantic-settings
   ```
3. Enable the safe JWT fallback and run the API (mock DB mode):
   ```powershell
   $env:USE_SIMPLE_JWT = '1'
   python -m uvicorn backend.main:app --reload --port 3000
   ```
4. Verify the API is running:
   - Health: http://localhost:3000/health
   - Register: POST http://localhost:3000/api/register (JSON payload)
   - Login: POST http://localhost:3000/api/login

Frontend (quick demo)

1. Install Node dependencies:
   ```bash
   cd frontend
   npm ci
   ```
2. Start the frontend dev server (defaults to port 5173):
   ```bash
   npm run dev
   ```
3. Open the UI at http://localhost:5173 and use the register/login flows; the frontend will call `http://localhost:3000/api` in development.

Running the test smoke suite locally

1. From the repo root (backend test runner):
   ```powershell
   .\.venv\Scripts\Activate.ps1
   $env:USE_SIMPLE_JWT = '1'
   python -m pytest backend/tests -q -k smoke
   ```

Notes

- The codebase supports a mock DB mode when `SUPABASE_URL` and `SUPABASE_ANON_KEY` are not set; this is ideal for quick demos and local development.
- For full integration testing you will need a Supabase/Postgres instance and the full set of requirements installed (see `backend/requirements.txt`).
