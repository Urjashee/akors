from typing import Optional, Any, List
from pydantic import BaseModel, EmailStr, Field

class AddProperty(BaseModel):
    token: str
    qei_number: str
    password: str

class UpdateStates(BaseModel):
    states: List[int]

class AddEditForms(BaseModel):
    id: Optional[int] = None
    name: str
    state_id: int