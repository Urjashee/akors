from typing import Optional, Any, List
from pydantic import BaseModel, EmailStr, Field

class AddProperty(BaseModel):
    id: Optional[str] = None
    name: str
    state_registration: str
    property_management_company: str
    address_line_1: str
    address_line_2: str
    city: str
    zipcode: str
    state_id: int

class AssignManager(BaseModel):
    property_id: int
    manager_id: int