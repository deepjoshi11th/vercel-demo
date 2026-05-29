from google import genai
from google.genai import types
import os
import json
from pathlib import Path
import time
import logging

from ..models import Question, BiJ
from ..config import supabase

# Setup logging
logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Construct paths relative to this file's location
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
SYSTEM_INSTRUCTION_PATH = BASE_DIR / "poc" / "gemini" / "system-instruction.md"
JUDGEMENT_INSTRUCTION_PATH = BASE_DIR / "poc" / "gemini" / "judgement-insturction.md"

# Load instructions with error handling
system_instruction = ""
try:
    if SYSTEM_INSTRUCTION_PATH.exists():
        with open(SYSTEM_INSTRUCTION_PATH, "r") as f:
            lines = f.readlines()
            for line in lines:
                system_instruction += line
    else:
        raise FileNotFoundError(f"System instruction file not found at {SYSTEM_INSTRUCTION_PATH}")
except Exception as e:
    raise Exception(f"Failed to load system instruction: {str(e)}")

judgement_instruction = ""
try:
    if JUDGEMENT_INSTRUCTION_PATH.exists():
        with open(JUDGEMENT_INSTRUCTION_PATH, "r") as f:
            judgement_instruction = f.read()
    else:
        raise FileNotFoundError(f"Judgement instruction file not found at {JUDGEMENT_INSTRUCTION_PATH}")
except Exception as e:
    raise Exception(f"Failed to load judgement instruction: {str(e)}")   

def get_previous_choices(gameId: str):
    response = supabase.table("question").select("text, selected, option1, option2, option3").eq("gameId", gameId).order("created_at", desc=True).execute()
    content = []
    if response.data:
        for question in response.data:
            if question['selected'] == 0:
                continue
            data = {
                "text": question['text'],
                "selected": question['option' + str(question['selected'])]
            }
            content.append(data)
        if len(content) > 0:
            formatted_content = json.dumps(content, indent=4)
            content = f"""Here are the previous choices for this project:
            
            previuous choices: ${formatted_content}
            """
        else:
            content = "I am starting fresh, I have no previous choices for this project."
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

def call_gemini_with_retry(
    model: str,
    contents: str,
    system_instruction: str,
    response_schema,
    max_retries: int = 3,
    initial_delay: float = 1.0
):
    """
    Call Gemini API with exponential backoff retry logic for handling transient failures.
    
    Args:
        model: Model name to use
        contents: Input content
        system_instruction: System instruction
        response_schema: Pydantic schema for response
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
    
    Returns:
        Parsed JSON response
    
    Raises:
        Exception: If all retries fail
    """
    client = genai.Client(api_key=GEMINI_API_KEY)
    delay = initial_delay
    last_error = None
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Gemini API call attempt {attempt + 1}/{max_retries} using model {model}")
            
            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_mime_type='application/json',
                    response_schema=response_schema,
                    system_instruction=system_instruction,
                    thinking_config=types.ThinkingConfig(
                        include_thoughts=False,
                        thinking_budget=0,
                    ) if "gemini" in model else None
                )
            )
            
            # Parse response based on model
            if "gemma" in model.lower():
                text = fix_gemma_4_response(response.text)
            else:
                text = response.text
                
            result = json.loads(text)
            logger.info(f"Gemini API call successful on attempt {attempt + 1}")
            return result
            
        except json.JSONDecodeError as e:
            last_error = f"JSON parsing error: {str(e)}"
            logger.warning(f"JSON parsing failed on attempt {attempt + 1}: {last_error}")
        except Exception as e:
            error_msg = str(e)
            last_error = error_msg
            
            # Check if it's a retryable error
            is_retryable = any([
                "500" in error_msg,
                "503" in error_msg,
                "429" in error_msg,  # Rate limit
                "RESOURCE_EXHAUSTED" in error_msg,
                "DEADLINE_EXCEEDED" in error_msg,
                "UNAVAILABLE" in error_msg,
                "timeout" in error_msg.lower(),
                "connection" in error_msg.lower(),
            ])
            
            if attempt < max_retries - 1 and is_retryable:
                logger.warning(f"Retryable error on attempt {attempt + 1}: {error_msg}. Retrying in {delay}s...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                logger.error(f"Non-retryable error or final attempt failed: {error_msg}")
                raise
    
    # If we get here, all retries failed
    raise Exception(f"Gemini API failed after {max_retries} attempts. Last error: {last_error}")

def generate_question(gameId: str):
    """Generate a new question using Gemini API with retry logic."""
    try:
        if not GEMINI_API_KEY:
            raise Exception("GEMINI_API_KEY environment variable is not set")
        
        content = get_previous_choices(gameId)
        # Use the more stable gemini-3-flash-preview model
        result = call_gemini_with_retry(
            model="gemma-4-31b-it",
            contents=content,
            system_instruction=system_instruction,
            response_schema=Question,
            max_retries=3,
            initial_delay=1.0
        )
        return result
    except Exception as e:
        logger.error(f"Failed to generate question for gameId {gameId}: {str(e)}")
        raise Exception(f"Failed to generate question: {str(e)}")
    
def generate_judgement(gameId: str):
    """Generate judgement using Gemini API with retry logic."""
    try:
        if not GEMINI_API_KEY:
            raise Exception("GEMINI_API_KEY environment variable is not set")
        
        content = get_previous_choices(gameId)
        # Use the more stable gemini-3-flash-preview model
        result = call_gemini_with_retry(
            model="gemma-4-31b-it",
            contents=content,
            system_instruction=judgement_instruction,
            response_schema=BiJ,
            max_retries=3,
            initial_delay=1.0
        )
        return result
    except Exception as e:
        logger.error(f"Failed to generate judgement for gameId {gameId}: {str(e)}")
        raise Exception(f"Failed to generate judgement: {str(e)}")