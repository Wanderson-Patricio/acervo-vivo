from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from ._base_class import BasePostgreSQLModel

class Authentication(BasePostgreSQLModel):
    __tablename__ = '"Authentication"'

    user_id: int
    hash_password: str
    last_time_altered: datetime
    failed_attempts: Optional[int] = 0
    is_blocked: Optional[bool] = False


    def user_id_validator(self, value: int):
        if (not isinstance(value, int)) or (value <= 0):
            raise ValueError("Authentication 'user_id' must be a positive integer.")
    
    def hash_password_validator(self, value: str):
        if (not value) or (not isinstance(value, str)):
            raise ValueError("Authentication 'hash_password' must be a non empty string.")
        
    def last_time_altered_validator(self, value: datetime):
        if (not isinstance(value, datetime)):
            raise ValueError("Authentication 'last_time_altered' must be a datetime object.")
        
    def failed_attempts_validator(self, value: Optional[int]):
        if value is not None and (not isinstance(value, int) or value < 0):
            raise ValueError("Authentication 'failed_attempts' must be a non-negative integer.")
        
    def is_blocked_validator(self, value: bool):
        if (not isinstance(value, bool)):
            raise ValueError("Authentication 'is_blocked' must be a boolean value.")
        

class AuthenticationCreate(BaseModel):
    user_id: int
    password: str

class AuthenticationUpdate(BaseModel):
    user_id: int
    password: str