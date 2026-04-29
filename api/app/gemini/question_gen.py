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


def fix_gemma_4_response(response_text: str) -> str:
    """
    Fixes the response from Gemma 4 to ensure it is valid JSON.
    This is a workaround for any formatting issues that may arise with the response.
    """
    try:
        json.loads(response_text)
        return response_text  # If parsing is successful, return the original text
    except json.JSONDecodeError:
        # If parsing fails, attempt to fix common issues
        # For example, ensure that keys and string values are enclosed in double quotes
        last_close_brace_index = response_text.rfind('}')
        if last_close_brace_index != -1:
            fixed_text = response_text[:last_close_brace_index + 1]
            return fixed_text
        else:
            raise Exception("Unable to fix the response from Gemma 4: No closing brace found.")

def generate_question(gameId: str):
    try:
        content = get_previous_choices(gameId)
        client = genai.Client(api_key=GEMINI_API_KEY)
        model = "gemma-4-31b-it"
        response = client.models.generate_content(
            model=model,
            # model="gemini-3-flash-preview",
            contents=content,
            config=types.GenerateContentConfig(
                response_mime_type='application/json',
                response_schema= Question,
                system_instruction=system_instruction
            )
        )
        if model == "gemma-4-31b-it":
            text = fix_gemma_4_response(response.text)
            return json.loads(text)
        return json.loads(response.text)
    except Exception as e:
        raise Exception(f"Failed to generate question: {str(e)}")