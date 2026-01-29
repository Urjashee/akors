from typing import Optional, Any
from pydantic import BaseModel, EmailStr, Field

class UserOutSchema(BaseModel):
    status: str
    message: Any
    data: Optional[Any]

class ErrorSchema(BaseModel):
    status: str
    message: str

class RegisterSchema(BaseModel):
    email: str
    password: str = Field(min_length=8)

    first_name: str
    last_name: str

    company_name: Optional[str] = None
    company_address: Optional[str] = None
    phone_number: Optional[str] = None

    title: Optional[int] = None
    subscription: Optional[int] = None

    qei_number: Optional[str] = None

    class Config:
        from_attributes = True

class VerifyEmailSchema(BaseModel):
    token: str
    user_id: int
    type: int
