from typing import Dict, Any
from app.database.models import engine, Story, Chapter
from sqlmodel import Session, select
from app.utils.file_system import write_chapter_to_disk, read_chapter_from_disk
import google.generativeai as genai
import os

# --- Tool Definitions ---

def save_chapter_draft(story_id: int, chapter_number: int, content: str, summary: str, title: str) -> str:
    """Saves a chapter draft to the database."""
    with Session(engine) as session:
        statement = select(Chapter).where(
            Chapter.story_id == story_id, 
            Chapter.chapter_number == chapter_number
        )
        existing = session.exec(statement).first()
        
        if existing:
            existing.content = content
            existing.summary = summary
            existing.title = title
            existing.status = "draft"
            session.add(existing)
        else:
            chapter = Chapter(
                story_id=story_id, 
                chapter_number=chapter_number,
                title=title,
                summary=summary,
                content=content,
                status="draft"
            )
            session.add(chapter)
        session.commit()
    return "Draft saved to database."

def get_story_context(story_id: int) -> str:
    """Retrieves the full story bible and outline."""
    with Session(engine) as session:
        story = session.get(Story, story_id)
        if not story:
            return "Story not found."
        return f"TITLE: {story.title}\nPREMISE: {story.premise}\nOUTLINE: {story.outline}\nCHARACTERS: {story.characters}"

def get_previous_chapters(story_id: int, current_chapter: int) -> str:
    """Retrieves summaries of previous chapters."""
    with Session(engine) as session:
        statement = select(Chapter).where(
            Chapter.story_id == story_id, 
            Chapter.chapter_number < current_chapter
        ).order_by(Chapter.chapter_number)
        chapters = session.exec(statement).all()
        return "\n".join([f"Chapter {c.chapter_number}: {c.summary}" for c in chapters])
