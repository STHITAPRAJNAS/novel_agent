# Novelist AI - Local Agentic Workflow

This project is a local-first, Human-in-the-Loop (HITL) storytelling engine using **Google ADK** (Agent Development Kit) and **Gemini 1.5 Pro**.

## Key Features

*   **Multi-Agent System:** Orchestrates Architect, Ghostwriter, and two Editor agents.
*   **Iterative Workflow:** Automated writing, critique, and revision cycles.
*   **Human-in-the-Loop (HITL):** Pauses for human intervention only at critical decision points (e.g., initial outline approval, critical editor feedback).
*   **Persistent Sessions:** Uses SQLite for persistent agent session history.
*   **Persistent Story Data:** Stores novel content (story details, chapters) in SQLite.
*   **Local File System Output:** Chapters saved as Markdown files.
*   **Book-Quality PDF Generation:** Automatically compiles chapters into a single Markdown and then a beautifully formatted PDF (pure Python, no Pandoc executable needed).
*   **ADK Dev UI Integration:** Interact with the agent via the standard ADK developer interface.

## Prerequisites

1.  **Python** (v3.11+) with `uv` installed (`pip install uv`)
2.  **Google API Key** (for Gemini models)

## Setup

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/STHITAPRAJNAS/novel_agent.git
    cd novel_agent
    ```

2.  **Backend:**
    ```bash
    cd backend
    uv sync
    ```
    Create a `.env` file in the `backend/` directory with your Google API Key:
    ```
    # .env
    GOOGLE_API_KEY=YOUR_GEMINI_API_KEY
    ```

## Running the Backend

This runs the FastAPI server which hosts the Novelist AI agent and the ADK Dev UI.

```bash
cd backend
uv run uvicorn app.server:app --reload --port 8000
```

Once the server is running, navigate to `http://localhost:8000/dev-ui` in your browser.

### Interacting with the Agent via Dev UI

1.  **Open `http://localhost:8000/dev-ui`**.
2.  Select `novelist_agent` from the list of available agents.
3.  Start by typing commands like:
    *   "Start a new fantasy novel about a lost princess."
    *   "Write chapter 1."
    *   "Approve the outline."
    *   "Proceed."
    *   The agent's prompts are designed to guide you through the workflow.

## Project Structure (Backend)

*   `backend/app/agent.py`: Defines the `novelist_agent` (root agent) and its sub-agents (Architect, Ghostwriter, Editor Alpha, Editor Beta), including their sophisticated prompts and tool assignments.
*   `backend/app/tools.py`: Contains Python functions wrapped as tools for agents (e.g., `save_chapter_draft`, `create_full_novel_pdf`, `editor_modify_and_save_chapter`).
*   `backend/app/server.py`: The FastAPI application that uses `google.adk.cli.fast_api.get_fast_api_app` to host the ADK agent, handle sessions, and provide the `/dev-ui`.
*   `backend/app/database/models.py`: Defines the SQLModel for storing novel content (Story, Chapter).
*   `backend/app/utils/file_system.py`: Utilities for reading/writing chapter files to disk.
*   `backend/app/services/sqlite_session.py`: (DELETED - ADK handles SQLite sessions internally now via `session_service_uri`).
*   `backend/data/sessions.db`: The SQLite database file for ADK's agent session history (created automatically).
*   `backend/novels/`: Directory where generated novel chapters (Markdown) and final PDFs are stored.

## Frontend

The frontend (Next.js/React) is not part of the current focus as per user request.

## Development Notes

*   **Session Management:** The ADK agent sessions are now persistent, stored in `backend/data/sessions.db`.
*   **LLM Model:** Uses `gemini-1.5-pro`.
*   **PDF Generation:** Uses pure Python libraries (`markdown-it-py` and `xhtml2pdf`) for robust, system-independent PDF creation.

---
**Note:** `uv run uvicorn app.server:app` is the entry point. The old `src/main.py` is no longer used.
---