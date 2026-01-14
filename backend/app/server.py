import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app
from fastapi.middleware.cors import CORSMiddleware # Keep CORS for potential future frontend
# from app.database.models import create_db_and_tables # Not needed directly in server.py, used by agent tools

load_dotenv()

# Setup minimal logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Directory where the agents reside
AGENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Configure SQLite session service
# This will be handled by the ADK framework
SESSION_SERVICE_URI = None # Use InMemorySessionService to avoid SQLite corruption

app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=True,
    session_service_uri=SESSION_SERVICE_URI,
    # memory_service_uri=SESSION_SERVICE_URI, # If agent.py uses memory service this way
    allow_origins=["*"], # For dev purposes
)
app.title = "Novelist AI"
app.description = "Agentic Workflow for Novel Writing"

@app.on_event("startup")
def on_startup():
    # create_db_and_tables() # This should be handled by the agent's init or when tools are used
    pass # ADK will initialize session db if it manages it.

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)