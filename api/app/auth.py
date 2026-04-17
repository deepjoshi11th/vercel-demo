"""Authentication endpoints."""
from fastapi import APIRouter, HTTPException, status, Depends
from .models import SignupRequest, LoginRequest, UserResponse
from .config import supabase
from .dependencies import get_current_user


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=dict)
async def signup(request: SignupRequest):
    """
    Sign up with email and password.
    """
    try:
        response = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password,
        })
        return {
            "user": {
                "id": response.user.id,
                "email": response.user.email,
            },
            "session": {
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token,
            } if response.session else None,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Signup failed: {str(e)}",
        )


@router.post("/login", response_model=dict)
async def login(request: LoginRequest):
    """
    Log in with email and password.
    """
    try:
        response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password,
        })
        return {
            "user": {
                "id": response.user.id,
                "email": response.user.email,
            },
            "session": {
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token,
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Login failed: {str(e)}",
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(user: dict = Depends(get_current_user)):
    """
    Get current authenticated user profile.
    """
    return UserResponse(
        id=user.id,
        email=user.email,
    )


@router.post("/logout")
async def logout():
    """
    Logout endpoint (token invalidation happens on client side).
    """
    return {"message": "Logged out successfully"}
