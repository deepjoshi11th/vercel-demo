from google import genai
from google.genai import types
import os
from pydantic import BaseModel

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

class Question(BaseModel):
    question: str
    answers: list[str]
    cont: bool

if __name__ == "__main__":
    client = genai.Client(api_key=GEMINI_API_KEY)
    system_instruction = ""
    with open("poc/system-instruction.md", "r") as f:
        lines = f.readlines()
        for line in lines:
            system_instruction += line
    print(system_instruction)
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents="I am working on a Java server which have the remove background functionality which is executed on backend, hosted on serverless platform like vercel. The image output is png files without watermark but with 512KB of input size limit. VCS is github.",
        config=types.GenerateContentConfig(
            response_mime_type='application/json',
            response_schema= Question,
            thinking_config=types.ThinkingConfig(
                include_thoughts=False,
                thinking_budget=0,
            ),system_instruction=system_instruction
        )
    )

    print(response.text)