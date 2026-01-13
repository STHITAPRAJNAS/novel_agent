import os

def write_chapter_to_disk(chapter_number: int, title: str, content: str, novel_title: str = "MyNovel"):
    """
    Writes the chapter content to a local file.
    """
    # Create directory if it doesn't exist
    directory = f"novels/{novel_title.replace(' ', '_')}"
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    filename = f"{directory}/chapter_{chapter_number}_{title.replace(' ', '_')}.md"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# Chapter {chapter_number}: {title}\n\n")
        f.write(content)
    
    return f"Successfully wrote chapter to {filename}"

def read_chapter_from_disk(chapter_number: int, title: str, novel_title: str = "MyNovel"):
    """
    Reads a chapter from disk.
    """
    directory = f"novels/{novel_title.replace(' ', '_')}"
    filename = f"{directory}/chapter_{chapter_number}_{title.replace(' ', '_')}.md"
    
    if not os.path.exists(filename):
        return "File not found."
        
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()
