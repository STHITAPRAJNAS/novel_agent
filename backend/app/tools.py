from typing import Dict, Any
from app.database.models import engine, Story, Chapter
from sqlmodel import Session, select
from app.utils.file_system import write_chapter_to_disk, read_chapter_from_disk
import google.generativeai as genai
import os
import subprocess # For pandoc
import re # For regex matching

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

def editor_modify_and_save_chapter(story_id: int, chapter_number: int, new_content: str, new_summary: str, new_title: str) -> str:
    """
    Allows an editor to directly modify a chapter's content, summary, and title, then saves it to the database and disk.
    This tool should be used when the editor believes a direct fix is more efficient than sending feedback to the ghostwriter.
    """
    with Session(engine) as session:
        statement = select(Chapter).where(
            Chapter.story_id == story_id, 
            Chapter.chapter_number == chapter_number
        )
        existing = session.exec(statement).first()
        
        if existing:
            existing.content = new_content
            existing.summary = new_summary
            existing.title = new_title
            existing.status = "edited" # Status updated to edited
            session.add(existing)
        else:
            return "Error: Chapter not found in database for direct modification."
        session.commit()
    
    # Save to disk as well
    story_context = get_story_context(story_id) # Need story title for disk saving
    novel_title = story_context.split('TITLE: ')[1].split('\n')[0].strip() if story_context.startswith('TITLE:') else "MyNovel"

    write_chapter_to_disk(chapter_number, new_title, new_content, novel_title)

    return f"Chapter {chapter_number} directly modified and saved by editor."

def create_full_novel_pdf(novel_title: str, story_id: int) -> str:
    """
    Consolidates all chapters for a given novel into a single Markdown file,
    then converts it to a professional-looking PDF using Pandoc.
    Requires Pandoc to be installed and in the system's PATH.
    """
    # 1. Gather all chapters and sort them
    script_dir = os.path.dirname(os.path.abspath(__file__)) # app/
    project_root = os.path.join(script_dir, '..', '..') # root/

    novel_dir = os.path.join(project_root, 'backend', 'novels', novel_title.replace(' ', '_'))
    
    chapter_files = []
    if not os.path.exists(novel_dir):
        return f"Error: Novel directory not found at {novel_dir}. No chapters to compile."

    for filename in os.listdir(novel_dir):
        if filename.startswith("chapter_") and filename.endswith(".md"):
            match = re.match(r"chapter_(\d+)_.*\.md", filename)
            if match:
                chapter_num = int(match.group(1))
                chapter_files.append((chapter_num, filename))

    chapter_files.sort(key=lambda x: x[0])

    # 2. Compile into a single Markdown file
    full_md_filename = os.path.join(project_root, f"{novel_title.replace(' ', '_')}_full_novel.md")
    
    with open(full_md_filename, "w", encoding="utf-8") as outfile:
        outfile.write(f"# {novel_title.replace('_', ' ').title()}\n\n")
        for chapter_num, filename in chapter_files:
            filepath = os.path.join(novel_dir, filename)
            with open(filepath, "r", encoding="utf-8") as infile:
                outfile.write(infile.read())
            outfile.write("\n\n---\n\n") # Separator between chapters

    # 3. Convert to PDF using Pandoc
    pdf_filename = os.path.join(project_root, f"{novel_title.replace(' ', '_')}_full_novel.pdf")
    
    try:
        # Use lualatex for better font handling and modern LaTeX features
        # Add some basic styling for book format
        subprocess.run(
            [
                "pandoc",
                full_md_filename,
                "-o",
                pdf_filename,
                "--pdf-engine=lualatex",
                "-V", "geometry:margin=1in", # 1 inch margins
                "-V", "fontsize=12pt",     # 12pt font size
                "-V", "mainfont=EB Garamond", # Example font, user might customize
                "-V", "linestretch=1.2",    # 1.2 line spacing
                "--toc",                    # Table of contents
                "--number-sections"         # Number sections (chapters)
            ],
            check=True,
            capture_output=True,
            text=True
        )
        return f"Successfully created PDF for '{novel_title}' at {pdf_filename}"
    except FileNotFoundError:
        return "Error: Pandoc not found. Please install Pandoc (https://pandoc.org/installing.html) to create PDF."
    except subprocess.CalledProcessError as e:
        return f"Error during PDF generation with Pandoc: {e.stderr}"
    except Exception as e:
        return f"An unexpected error occurred during PDF creation: {e}"
