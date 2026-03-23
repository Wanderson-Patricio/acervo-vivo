from typing import Optional

from pydantic import BaseModel

from ._base_class import BasePostgreSQLModel

class Role(BasePostgreSQLModel):
    __tablename__ = '"Roles"'

    name: str
    access_level: int
    description: str

    def name_validator(self, value: str):
        if (not value) or (not isinstance(value, str)) or (len(value) > 255):
            raise ValueError("Role name must be a non empty string with at most 255 characters.")
    
    def access_level_validator(self, value: int):
        if (not isinstance(value, int)) or (value < 0):
            raise ValueError(f"Role access_level must be a non-negative integer or None. given {value} instead.")
        
    def description_validator(self, value: str):
        if (not value) or (not isinstance(value, str)):
            raise ValueError("Role description must be a non empty string.")
        

class RoleCreate(BaseModel):
    name: str
    access_level: int
    description: str


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    access_level: Optional[int] = None
    description: Optional[str] = None