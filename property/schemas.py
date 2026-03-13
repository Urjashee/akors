from typing import Optional, Any, List

from ninja import Schema
from pydantic import BaseModel, EmailStr, Field

class AddProperty(BaseModel):
    id: Optional[int] = None
    manager_id: Optional[int] = None
    name: str
    state_registration: str
    property_management_company: str
    address_line_1: str
    address_line_2: str
    city: str
    zipcode: str
    state_id: int
    forms: Optional[List[int]] = None

class AssignManager(BaseModel):
    property_id: int
    manager_id: int

class StateSchema(Schema):
    id: int
    name: str


class PropertyFormSchema(Schema):
    id: int
    name: str
    image: str | None = None
    active: int


class PropertySchema(Schema):
    id: int
    name: str
    address_line_1: str
    address_line_2: str
    city: str
    zipcode: str
    property_management_company: str
    state_registration: str
    state: StateSchema
    forms: list[PropertyFormSchema]
