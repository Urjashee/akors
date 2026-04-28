from datetime import datetime
from typing import Optional, Any, List
from ninja import Schema
from pydantic import BaseModel, EmailStr, Field
from property.models import UnitType

class StateSchema(Schema):
    id: int
    name: str

class UploadUnitImage(BaseModel):
    unit_id: int = None

class UploadUnitForm(BaseModel):
    unit_id: int
    form_name: str
    expiration_date: Optional[datetime] = None

class UnitTypeSchema(Schema):
    id: int
    name: str

class UnitClassSchema(Schema):
    id: int
    name: str

class CreatedBySchema(Schema):
    id: int
    email: str

class UnitFormSchema(Schema):
    id: int
    url: Optional[str] = None
    form_name: str
    expiration_date: datetime | None

class UnitImageSchema(Schema):
    id: int
    url: Optional[str] = None

class AddProperty(BaseModel):
    id: Optional[int] = None
    manager_id: Optional[int] = None
    name: str
    # state_registration: str
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

class PropertyFormSchema(Schema):
    id: int
    name: str
    image: str | None = None
    unit_type: str | None = None
    active: Optional[int] = None

class ManagerSchema(Schema):
    id: int
    first_name: str
    last_name: str
    email: str

class PropertySchema(Schema):
    id: int
    name: str
    address_line_1: str
    address_line_2: str
    city: str
    zipcode: str
    property_management_company: str
    # state_registration: str
    state: StateSchema
    manager: Optional[ManagerSchema] = None
    forms: list[PropertyFormSchema]
    unit_count: int

class PropertyListData(Schema):
    properties: List[PropertySchema]
    current_page: int
    page_size: int
    total: int
    total_pages: int

class AddEditUnit(BaseModel):
    id: Optional[int] = None
    state_registration: str
    nickname: str
    expiration_date: Optional[datetime] = None
    unit_type: int
    unit_class: int
    property: int

class UnitPropertySchema(Schema):
    id: int
    name: str
    state_registration: str
    property_management_company: str
    address_line_1: str
    address_line_2: str
    city: str
    zipcode: str
    state: StateSchema

class UnitSchema(Schema):
    id: int
    nickname: str
    state_registration: str | None
    expiration_date: datetime | None
    certificate: str | None
    unit_type: UnitTypeSchema | None
    unit_class: UnitClassSchema | None
    user: CreatedBySchema | None
    property: UnitPropertySchema | None
    forms: List[UnitFormSchema] | None
    images: List[UnitImageSchema] | None
    forms_count: int | None = 0
    images_count: int | None = 0


class UnitListData(Schema):
    units: List[UnitSchema]
    current_page: int
    page_size: int
    total: int
    total_pages: int






