import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel('gemini-1.5-pro')

def generate_story_outline(premise: str, genre: str) -> str:
    prompt = f"""
    You are an expert novel architect. 
    Genre: {genre}
    Premise: {premise}
    
    Create a detailed chapter-by-chapter outline for a 10-chapter novel based on this premise.
    Include a brief summary for each chapter.
    Format your response as a structured list.
    """
    response = model.generate_content(prompt)
    return response.text

def generate_character_sheets(premise: str) -> str:
    prompt = f"""
    You are an expert character designer.
    Premise: {premise}
    
    Create detailed character sheets for the main protagonist, antagonist, and one supporting character.
    Include Name, Role, Motivation, Flaws, and Physical Description.
    """
    response = model.generate_content(prompt)
    return response.text