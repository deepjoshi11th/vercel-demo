import uuid
from fastapi import APIRouter, HTTPException, status, Depends
from .models import Game, Question
from .dependencies import get_current_user
from .config import supabase
from .gemini.question_gen import generate_question as gen_q

router = APIRouter(prefix="/api/game", tags=["game"])

@router.post("")
async def create_game(
    user: dict = Depends(get_current_user)
):
    """
    Create game for authenticated user.
    Uses RLS to ensure users can only modify their own data.
    """
    try:
        response = supabase.table("game").upsert({
            "userId": user.id,
            "gameid": str(uuid.uuid4())
        }, on_conflict="userId").execute()

        if response.data:
            return {
                "success": True,
                "data": response.data[0]
            }
        else:
            raise Exception("Failed to create new game")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update profile details: {str(e)}",
        )

@router.get("")
async def get_current_game(user: dict = Depends(get_current_user)):
    """
    Get current game id for authenticated user.
    RLS ensures users can only see their own data.
    """
    try:
        response = supabase.table("game").select("*").eq("userId", user.id).execute()

        if response.data:
            return {
                "success": True,
                "data": {
                    "gameId": response.data[0]["gameid"],
                    "userId": response.data[0]["userId"]
                }
            }
        else:
            return {
                "success": True,
                "data": None
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to fetch current game: {str(e)}",
        )

@router.post("/questions/{gameId}")
async def add_question(
    request: Question,
    gameId: str,
    user: dict = Depends(get_current_user)
):
    """
    Add question to a game for authenticated user.
    Uses RLS to ensure users can only modify their own data.
    """
    try:
        response = supabase.table("question").insert({
            "text": request.text,
            "option1": request.options[0],
            "option2": request.options[1],
            "option3": request.options[2],
            "selected": 0,
            "gameId": gameId,
        }).execute()

        if response.data:
            return {
                "success": True,
                "data": {
                    "id": response.data[0]["id"],
                    "gameId": response.data[0]["gameId"]
                }
            }
        else:
            raise Exception("Failed to add question to game")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update profile details: {str(e)}",
        )

@router.post("/questions/generate/{gameId}")
async def generate_question(
    gameId: str,
    user: dict = Depends(get_current_user)
):
    """
    Generate a new question for a game.
    """
    if not gameId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Game ID is required to generate question",
        )
    try:
        question = gen_q(gameId)
        response = supabase.table("question").insert({
            "text": question['text'],
            "option1": question['options'][0],
            "option2": question['options'][1],
            "option3": question['options'][2],
            "selected": 0,
            "gameId": gameId,
        }).execute()

        if response.data:
            return {
                "success": True,
                "data": {
                    "id": response.data[0]["id"],
                    "gameId": response.data[0]["gameId"],
                    "text": response.data[0]["text"],
                    "options": [response.data[0]["option1"], response.data[0]["option2"], response.data[0]["option3"]],
                    "selected": response.data[0]["selected"],
                    "cont": question['cont'] 
                }
            }
        else:
            raise Exception("Failed to add question to game")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to generate question for game {gameId}: {str(e)}",
        )

@router.get("/questions/{gameId}")
async def get_questions_for_game(
    gameId: str,
    user: dict = Depends(get_current_user)
):
    """
    Get questions for a specific game.
    RLS ensures users can only see their own data.
    """
    try:
        response = supabase.table("question").select("*").eq("gameId", gameId).execute()

        if response.data:
            return {
                "success": True,
                "data": response.data
            }
        else:
            return {
                "success": True,
                "data": None
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to fetch current game: {str(e)}",
        )
    
@router.patch("/answer/{questionId}")
async def select_answer(
    answer: str,
    questionId: str,
    user: dict = Depends(get_current_user)
):
    """
    Select an answer for a question in a game for authenticated user.
    Uses RLS to ensure users can only modify their own data.
    """
    try:
        response = supabase.table("question").select("*").eq("id", questionId).execute()
        if not response.data:
            raise Exception("Question not found")
        question = response.data[0]
        if answer not in [question["option1"], question["option2"], question["option3"]]:
            raise Exception("Invalid answer option")
        ind = [question["option1"], question["option2"], question["option3"]].index(answer) + 1
        response = supabase.table("question").update({
            "selected": ind,
        }).eq("id", questionId).execute()

        if response.data:
            return {
                "success": True,
                "data": response.data
            }
        else:
            raise Exception("Failed to select answer for question")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to select answer for question {questionId}: {str(e)}",
        )
