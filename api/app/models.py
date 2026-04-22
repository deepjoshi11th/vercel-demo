"""Pydantic models for request/response validation."""
from pydantic import BaseModel


class SignupRequest(BaseModel):
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: str
    email: str


class ProfileDetailsRequest(BaseModel):
    sensitive_part: str


class ProfileDetailsResponse(BaseModel):
    id: str
    sensitive_part: str

class QRCodeRequest(BaseModel):
    text: str
    size: int = 5
    back_color: str = "#000000"
    fill_color: str = "#FFFFFF"