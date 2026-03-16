from datetime import datetime
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
    unit_type: str | None = None
    active: Optional[int] = None


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

class AddEditUnit(BaseModel):
    id: Optional[int] = None
    state_registration: str
    nickname: str
    expiration_date: Optional[datetime] = None
    unit_type: int
    unit_class: int
    property: int

class UploadUnitImage(BaseModel):
    unit_id: int = None

class UploadUnitForm(BaseModel):
    unit_id: int
    form_name: str
    expiration_date: Optional[datetime] = None


