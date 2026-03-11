from typing import Optional, Any, List
from pydantic import BaseModel, EmailStr, Field

class AddProperty(BaseModel):
    token: str
    qei_number: str
    password: str