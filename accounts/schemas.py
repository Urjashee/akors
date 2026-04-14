from datetime import datetime
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

class ChangePasswordSchema(BaseModel):
    old_password: str
    password: str

class EmailSchema(BaseModel):
    email: str

class ApproveDenySchema(BaseModel):
    user_id: int
    status: str

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

class EditPropertyManager(BaseModel):

    first_name: str
    last_name: str

    company_name: Optional[str] = None
    company_address: Optional[str] = None
    phone_number: Optional[str] = None


# --- Admin user list schemas ---

from typing import List  # noqa: E402


class RoleSchema(Schema):
    id: int
    name: str


class SubscriptionSchema(Schema):
    id: Optional[int] = None
    name: Optional[str] = None
    amount: Optional[float] = None


class UserAdminSchema(Schema):
    id: int
    email: str
    first_name: str
    last_name: str
    email_verified_at: Optional[datetime] = None
    status: str
    company_name: Optional[str] = None
    company_address: Optional[str] = None
    phone_number: Optional[str] = None
    role: RoleSchema
    subscription: SubscriptionSchema


class AdminUserListData(Schema):
    pending_users_count: int
    users: List[UserAdminSchema]
    current_page: int
    page_size: int
    total: int
    total_pages: int


# --- Property manager user list schemas ---

class TitleSchema(Schema):
    id: int
    name: str


class PMUserSchema(Schema):
    id: int
    email: str
    first_name: str
    last_name: str
    status: str
    title: TitleSchema


class PMUserListData(Schema):
    users: List[PMUserSchema]
    current_page: int
    page_size: int
    total: int
    total_pages: int
