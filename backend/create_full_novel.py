import os
import re

script_dir = os.path.dirname(os.path.abspath(__file__)) # This is backend/
project_root = os.path.join(script_dir, '..') # This is novel_agent/

novel_title = "The_son_of_the_soil"
novel_dir = os.path.join(script_dir, 'novels', novel_title) # Correct: novels is inside backend/
output_filename = os.path.join(project_root, f"{novel_title}_full_novel.md")

chapter_files = []
if not os.path.exists(novel_dir):
    print(f"Error: Novel directory not found at {novel_dir}")
else:
    for filename in os.listdir(novel_dir):
        if filename.startswith("chapter_") and filename.endswith(".md"):
            match = re.match(r"chapter_(\d+)_.*\.md", filename)
            if match:
                chapter_num = int(match.group(1))
                chapter_files.append((chapter_num, filename))

    # Sort chapters by number
    chapter_files.sort(key=lambda x: x[0])

    full_novel_content = f"# {novel_title.replace('_', ' ').title()}\n\n"

    for chapter_num, filename in chapter_files:
        filepath = os.path.join(novel_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            full_novel_content += content + "\n\n"

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(full_novel_content)

    print(f"Successfully created {output_filename}")
