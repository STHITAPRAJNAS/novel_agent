import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app

load_dotenv()

# Setup minimal logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Directory where the agents reside
AGENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 

# In-memory session configuration
session_service_uri = None

from app.database.models import create_db_and_tables

app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=True,
    session_service_uri=session_service_uri,
)
app.title = "Novelist AI"
app.description = "Agentic Workflow for Novel Writing"

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)