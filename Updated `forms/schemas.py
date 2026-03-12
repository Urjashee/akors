from typing import Optional, Any, List
from pydantic import BaseModel, EmailStr, Field

class AddEditForms(BaseModel):
    id: Optional[int] = None
    name: Optional[str]
    state_id: Optional[int]

class DeleteForm(BaseModel):
    id: int
