# Novelist AI - Local Agentic Workflow

This project is a local-first, Human-in-the-Loop (HITL) storytelling engine using **Google ADK** (Agent Development Kit) and **Gemini 1.5 Pro**.

## Prerequisites

1.  **Node.js** (v18+)
2.  **Python** (v3.11+) with `uv` installed (`pip install uv`)
3.  **Google API Key** (Gemini)

## Setup

1.  **Backend:**
    ```bash
    cd backend
    uv sync
    ```
    Create a `.env` file in `backend/` with `GOOGLE_API_KEY=AIzaSy...`.

2.  **Frontend:**
    ```bash
    cd frontend
    npm install
    ```

## Running the Application

### Option 1: Full Application (Recommended)
This runs the custom FastAPI server which includes the Agent, the Database, and the Custom Endpoints (like `/story/create`).

```bash
cd backend
uv run uvicorn src.main:app --reload --port 8000
```

### Option 2: ADK Dev UI (Agent Only)
If you want to debug the agent isolation using the native ADK tools:

```bash
cd backend/src/novel_agent
# You might need to set PYTHONPATH to the project root
$env:PYTHONPATH = "C:\Users\papus\Developer\local_learning\novel_agent\backend"
adk web .
```

### Frontend
```bash
cd frontend
npm run dev
```
Open `http://localhost:3000`.

## Architecture
-   **Agent:** `backend/src/novel_agent` (Google ADK Native)
-   **Server:** `backend/src/main.py` (FastAPI + ADK `get_fast_api_app`)
-   **Database:** `backend/src/database` (SQLite + SQLModel)
-   **Tools:** `backend/src/novel_agent/tools.py`