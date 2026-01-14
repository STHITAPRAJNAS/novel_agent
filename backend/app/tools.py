from typing import Dict, Any
from app.database.models import engine, Story, Chapter
from sqlmodel import Session, select
from app.utils.file_system import write_chapter_to_disk, read_chapter_from_disk
import google.generativeai as genai
import os
import re # For regex matching

from markdown_it import MarkdownIt
from xhtml2pdf import pisa
import io # For PDF generation

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
    novel_title_from_context = story_context.split('TITLE: ')[1].split('\n')[0].strip() if story_context.startswith('TITLE:') else "MyNovel"

    write_chapter_to_disk(chapter_number, new_title, new_content, novel_title_from_context)

    return f"Chapter {chapter_number} directly modified and saved by editor."

def create_full_novel_pdf(story_id: int) -> str:
    """
    Consolidates all chapters for a given story_id into a single Markdown file,
    converts it to HTML, and then renders it to a professional-looking PDF.
    This tool uses pure Python libraries (markdown-it-py, xhtml2pdf) and does not require Pandoc.
    """
    with Session(engine) as db_session:
        story = db_session.get(Story, story_id)
        if not story:
            return f"Error: Story with ID {story_id} not found."
        novel_title = story.title.replace(' ', '_')
        display_novel_title = story.title
        
    # 1. Gather all chapters and sort them
    script_dir = os.path.dirname(os.path.abspath(__file__)) # app/
    project_root = os.path.join(script_dir, '..', '..') # root/

    novel_dir = os.path.join(project_root, 'backend', 'novels', novel_title)
    
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

    # 2. Compile into a single Markdown string
    md = MarkdownIt()
    
    full_md_filename = os.path.join(novel_dir, f"{novel_title}_full_novel.md") # Save in novel_dir
    
    with open(full_md_filename, "w", encoding="utf-8") as outfile:
        outfile.write(f"# {display_novel_title}\n\n")
        for chapter_num, filename in chapter_files:
            filepath = os.path.join(novel_dir, filename)
            with open(filepath, "r", encoding="utf-8") as infile:
                outfile.write(infile.read())
            outfile.write("\n\n---\n\n") # Separator between chapters

    # 3. Convert Markdown to HTML
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{display_novel_title}</title>
        <style>
            @page {{
                size: a4 portrait;
                margin: 1in;
                @frame footer {{
                    -pdf-frame-content: footerContent;
                    bottom: 0.5in;
                    margin-left: 1in;
                    margin-right: 1in;
                    height: 0.5in;
                }}
            }}
            body {{ font-family: \"serif\"; }}
            h1 {{ text-align: center; page-break-after: always; }}
            h2, h3, h4, h5, h6 {{ page-break-before: auto; }}
            .chapter-separator {{ page-break-after: always; }}
            pre {{ background-color: #eee; padding: 1em; overflow: auto; }}
        </style>
    </head>
    <body>
        <div id="footerContent" style="text-align: right; font-size: 10pt;">
            <p>- <pdf:pagenumber> -</p>
        </div>
        {md.render(full_md_content)}
    </body>
    </html>
    """

    # 4. Convert HTML to PDF using xhtml2pdf
    pdf_filename = os.path.join(novel_dir, f"{novel_title}_full_novel.pdf") # Save in novel_dir
    
    try:
        with open(pdf_filename, "wb") as pdf_file:
            pisa_status = pisa.CreatePDF(
                html_content,                # the HTML to convert
                dest=pdf_file                # file handle to receive result
            )
        
        if pisa_status.err:
            return f"Error during PDF generation: {pisa_status.err}"
        return f"Successfully created PDF for '{display_novel_title}' at {pdf_filename}"
    except Exception as e:
        return f"An unexpected error occurred during PDF creation: {e}"