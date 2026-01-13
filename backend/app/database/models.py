from typing import Optional, List
from sqlmodel import Field, SQLModel, create_engine, Session

class Story(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    genre: str
    premise: str
    outline: Optional[str] = None
    characters: Optional[str] = None # JSON string

class Chapter(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    story_id: int = Field(foreign_key="story.id")
    chapter_number: int
    title: str
    summary: str
    content: Optional[str] = None
    status: str = Field(default="draft") # draft, written, edited, approved

sqlite_file_name = "novel_agent.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
