import logging
from google.adk.agents import Agent
from app.tools import save_chapter_draft, get_story_context, get_previous_chapters, write_chapter_to_disk
import os

logger = logging.getLogger(__name__)

MODEL = "gemini-2.5-flash"

# --- Sub Agents ---

architect = Agent(
    name="architect",
    model=MODEL,
    description="Generates story outlines, character sheets, and high-level plot points.",
    instruction="""
    You are the Architect. Your goal is to build the structure of the novel.
    When asked to create a story, generating a detailed 10-chapter outline and character sheets.
    Always ensure the genre conventions are met.
    """
)

ghostwriter = Agent(
    name="ghostwriter",
    model=MODEL,
    description="Writes the actual prose for chapters based on outlines.",
    instruction="""
    You are the Ghostwriter. You write chapter content.
    1. Always retrieve the 'Story Context' and 'Previous Chapters' before writing.
    2. Write engaging, show-don't-tell prose.
    3. Use the 'save_chapter_draft' tool to save your work to the DB.
    4. Use the 'write_chapter_to_disk' tool to save a local markdown file.
    """,
    tools=[get_story_context, get_previous_chapters, save_chapter_draft, write_chapter_to_disk]
)

editor = Agent(
    name="editor",
    model=MODEL,
    description="Critiques drafts and ensures consistency.",
    instruction="""
    You are the Editor. You review drafts produced by the Ghostwriter.
    Check for:
    - Plot holes
    - Character inconsistencies
    - Pacing issues
    Provide constructive feedback.
    """
)

# --- Root Agent ---

root_agent = Agent(
    name="novelist_agent",
    model=MODEL,
    description="The Chief Editor managing the creation of a novel. Delegates to Architect, Ghostwriter, and Editor.",
    instruction="""
    You are the Novelist AI Manager.
    1. If the user wants to start a new story, ask the Architect to design it.
    2. If the user wants to write a chapter, ask the Ghostwriter.
    3. If the user wants a review, ask the Editor.
    
    Coordinate the team to produce a high-quality novel.
    """,
    sub_agents=[architect, ghostwriter, editor]
)

logger.info(f"✅ Agent '{root_agent.name}' created.")