from typing import Optional, Any, List
from pydantic import BaseModel, EmailStr, Field
from ninja import Schema

class AddProperty(BaseModel):
    token: str
    qei_number: str
    password: str

class UpdateStates(BaseModel):
    states: List[int]

class AddEditForms(BaseModel):
    id: Optional[int] = None
    name: Optional[str]
    state_id: Optional[int]

class DeleteForm(BaseModel):
    id: int


class DeleteState(BaseModel):
    id: int


class FormItemSchema(Schema):
    id: int
    name: str
    state_id: int
    image: str = None


class FormsListData(Schema):
    forms: List[FormItemSchema]
    current_page: int
    page_size: int
    total: int
    total_pages: int