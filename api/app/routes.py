"""Protected data endpoints."""
from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from .models import ProfileDetailsRequest
from .config import supabase, SUPABASE_URL, SUPABASE_KEY
from .dependencies import get_current_user, get_auth_header
from supabase import create_client


router = APIRouter(prefix="/api", tags=["data"])


@router.get("/data")
async def get_sample_data(authorization: str = Depends(get_auth_header)):
    """
    Get all sample data (requires authentication).
    RLS policies on sample_table will restrict data based on user context.
    """
    try:
        user = await get_current_user(authorization)
        # Create client with user's token for RLS to apply
        user_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        response = user_client.table("sample_table").select("*").execute()
        data = response.data
        return {
            "data": data,
            "total": len(data),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to fetch data: {str(e)}",
        )


@router.get("/items/{item_id}")
async def get_item(item_id: int, authorization: str = Depends(get_auth_header)):
    """
    Get specific item by ID (requires authentication).
    RLS policies will enforce user access control.
    """
    try:
        user = await get_current_user(authorization)
        user_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        response = user_client.table("sample_table").select("*").eq("id", item_id).execute()
        data = response.data
        if data:
            item = data[0]
            return {
                "item": item,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        else:
            return {"error": "Item not found"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to fetch item: {str(e)}",
        )


@router.post("/profile-details")
async def update_profile_details(
    request: ProfileDetailsRequest,
    authorization: str = Depends(get_auth_header)
):
    """
    Create or update profile details for authenticated user.
    Uses RLS to ensure users can only modify their own data.
    """
    try:
        user = await get_current_user(authorization)
        user_client = create_client(SUPABASE_URL, SUPABASE_KEY)

        # Upsert profile details - insert if doesn't exist, update if it does
        response = user_client.table("profile_details").upsert({
            "id": user.id,
            "sensetive_part": request.sensitive_part
        }).execute()

        if response.data:
            return {
                "success": True,
                "data": {
                    "id": response.data[0]["id"],
                    "sensitive_part": response.data[0]["sensetive_part"]
                },
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        else:
            raise Exception("Failed to save profile details")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update profile details: {str(e)}",
        )


@router.get("/profile-details")
async def get_profile_details(authorization: str = Depends(get_auth_header)):
    """
    Get profile details for authenticated user.
    RLS ensures users can only see their own data.
    """
    try:
        user = await get_current_user(authorization)
        user_client = create_client(SUPABASE_URL, SUPABASE_KEY)

        response = user_client.table("profile_details").select("*").eq("id", user.id).execute()

        if response.data:
            return {
                "success": True,
                "data": {
                    "id": response.data[0]["id"],
                    "sensitive_part": response.data[0]["sensetive_part"]
                },
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        else:
            return {
                "success": True,
                "data": None,
                "message": "No profile details found",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to fetch profile details: {str(e)}",
        )
