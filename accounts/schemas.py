from typing import Optional, Any
from pydantic import BaseModel, EmailStr, Field

class SuccessSchema(BaseModel):
    status: str
    message: str
    data: Optional[Any] = None

    class Config:
        exclude_none = True

class ErrorSchema(BaseModel):
    status: str
    message: str

class RegisterSchema(BaseModel):
    email: str
    password: Optional[str] = None

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
    password: Optional[str] = None

class EmailSchema(BaseModel):
    email: str

class LoginSchema(BaseModel):
    email: str
    password: str

class UserFilterSchema(BaseModel):
    status: Optional[str] = None

class CreatePasswordSchema(BaseModel):
    token: str
    password: str
    type: int
