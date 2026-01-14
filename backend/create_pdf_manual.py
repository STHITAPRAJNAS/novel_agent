import argparse
import os
import sys

# Add backend directory to sys.path to allow imports from app.
script_dir = os.path.dirname(os.path.abspath(__file__)) # This is backend/
project_root = os.path.join(script_dir, '..') # This is novel_agent/
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Force the creation of the database if it doesn't exist, as this script runs standalone.
# This mimics what @app.on_event("startup") does in app.server.py
try:
    from app.database.models import create_db_and_tables
    create_db_and_tables()
except Exception as e:
    print(f"Warning: Could not initialize database tables. PDF generation might fail if database is not set up: {e}")

from app.tools import create_full_novel_pdf

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manually create a full novel PDF.")
    parser.add_argument("--story_id", type=int, help="The ID of the story to generate PDF for (from DB).")
    parser.add_argument("--novel_title", type=str, help="The novel title string (used if story_id lookup fails or is not provided).")
    
    args = parser.parse_args()

    if args.story_id is None and args.novel_title is None:
        print("Error: Either --story_id or --novel_title must be provided.")
        sys.exit(1)

    result = create_full_novel_pdf(story_id=args.story_id, novel_title_str=args.novel_title)
    print(result)