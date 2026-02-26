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

class CreateCustomerSchema(BaseModel):
    email: str
    name: str

class CreateSubscriptionSchema(BaseModel):
    customer_id: str
    price_id: str
    subscription_type: int