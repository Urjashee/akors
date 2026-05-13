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
    id: int
    manager_id: Optional[int] = None
    name: Optional[str] = None
    # state_registration: str
    property_management_company: Optional[str] = None
    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None
    city: Optional[str] = None
    zipcode: Optional[str] = None
    state_id: Optional[str] = None
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
    has_visible_units: Optional[bool] = None

class PropertyListData(Schema):
    properties: List[PropertySchema]
    current_page: int
    page_size: int
    total: int
    total_pages: int

class UnitFields(BaseModel):
    state_registration: str
    nickname: Optional[str] = None
    unit_type: Optional[int] = None
    unit_class: Optional[int] = None


class AddEditUnit(UnitFields):
    id: int = None
    expiration_date: Optional[datetime] = None
    property: int

class UnitPropertySchema(Schema):
    id: int
    name: str
    state_registration: str | None
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


class AddUnitByAddress(UnitFields):
    address_line_1: str
    address_line_2: Optional[str] = None
    city: str
    zipcode: Optional[str] = None
    state_id: int


class AddUnitByAddressResponse(Schema):
    unit_id: int
    property_id: int
    property_name: str
    property_created: bool


class AssignFormToImage(BaseModel):
    form_id: int

class UnitVisibilityItemSchema(Schema):
    unit_id: int
    visibility: bool


class VisibilitySchema(Schema):
    units: List[UnitVisibilityItemSchema]







