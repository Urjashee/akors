from typing import Optional, Any, Generic, TypeVar, Type

from ninja import Schema
from pydantic import BaseModel, EmailStr, Field

T = TypeVar("T")

class SuccessSchema(Schema, Generic[T]):
    status: str
    message: str
    data: T

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

class InvitedUsers(BaseModel):
    first_name: str
    last_name: str
    email: str
    title: int

class SetupAccount(BaseModel):
    token: str
    qei_number: str
    password: str
