from google import genai
from google.genai import types
import os
import json

from ..models import Question
from ..config import supabase

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
system_instruction = ""
with open("poc/gemini/system-instruction.md", "r") as f:
    lines = f.readlines()
    for line in lines:
        system_instruction += line


def get_previous_choices(gameId: str):
    response = supabase.table("question").select("*").eq("gameId", gameId).execute()
    content = []
    if response.data:
        for question in response.data:
            data = {
                "text": question['text'],
                "option1": question['option1'],
                "option2": question['option2'],
                "option3": question['option3'],
                "selected": question['selected']
            }
            content.append(data)
        formatted_content = json.dumps(content, indent=4)
        content = f"""Here are the previous choices for this project:
        
        previuous choices: ${formatted_content}
        """
    else:
        return "I am starting fresh, I have no previous choices for this project."
    return content


def generate_question(gameId: str):
    content = get_previous_choices(gameId)
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    response = client.models.generate_content(
        model="gemma-4-31b-it",
        contents=content,
        config=types.GenerateContentConfig(
            response_mime_type='application/json',
            response_schema= Question,
            system_instruction=system_instruction
        )
    )
    return json.loads(response.text)