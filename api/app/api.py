"""Protected data endpoints."""
from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from datetime import datetime
from .models import ProfileDetailsRequest, QRCodeRequest
from .config import supabase
from .dependencies import get_current_user
import qrcode
import os
import tempfile
from fastapi.responses import FileResponse


router = APIRouter(prefix="/api", tags=["data"])


@router.get("/data")
async def get_sample_data(user: dict = Depends(get_current_user)):
    """
    Get all sample data (requires authentication).
    RLS policies on sample_table will restrict data based on user context.
    """
    try:
        response = supabase.table("sample_table").select("*").execute()
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
async def get_item(item_id: int, user: dict = Depends(get_current_user)):
    """
    Get specific item by ID (requires authentication).
    RLS policies will enforce user access control.
    """
    try:
        response = supabase.table("sample_table").select("*").eq("id", item_id).execute()
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


@router.get("/profile-details")
async def get_profile_details(user: dict = Depends(get_current_user)):
    """
    Get profile details for authenticated user.
    RLS ensures users can only see their own data.
    """
    try:
        response = supabase.table("profile_details").select("*").eq("id", user.id).execute()

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


@router.post("/profile-details")
async def update_profile_details(
    request: ProfileDetailsRequest,
    user: dict = Depends(get_current_user)
):
    """
    Create or update profile details for authenticated user.
    Uses RLS to ensure users can only modify their own data.
    """
    try:
        response = supabase.table("profile_details").upsert({
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

@router.post("/qr")
async def convert_to_qr(
    request: QRCodeRequest, 
    background_tasks: BackgroundTasks):
    """
    API to convert link to QR code. Take test from 
    request and other non-required param from request body 
    and converts it to qr code responses as png.
    """
    try:
        text = request.text
        if not text:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Request body must include a 'text' field."
            )
        box_size = request.size
        fill_color = request.fill_color
        back_color = request.back_color


        qr = qrcode.QRCode(
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=box_size,
            border=4,
        )
        if not text.startswith("https://") and not text.startswith("http://"):
            text = "https://" + text 
        qr.add_data(text)

        img = qr.make_image(fill_color=fill_color, back_color=back_color)

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
            tmp_path = tmp_file.name
        img.save(tmp_path, format="PNG")

        def _cleanup_file(path: str) -> None:
            try:
                os.remove(path)
            except OSError:
                pass

        background_tasks.add_task(_cleanup_file, tmp_path)

        return FileResponse(
            tmp_path,
            media_type="image/png",
            filename="qrcode.png",
        )
    except HTTPException:
        raise
    except ImportError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"QR code generation dependency missing: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to convert to QR code: {str(e)}"
        )
