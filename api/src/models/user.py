from datetime import date, datetime, timezone
from typing import Optional
from pydantic import BaseModel

from ._base_class import BasePostgreSQLModel

def normalize_datetime(value: datetime) -> datetime:
    """Converte um datetime para UTC e offset-naive."""
    if value.tzinfo is not None:
        value = value.astimezone(timezone.utc).replace(tzinfo=None)
    return value

class User(BasePostgreSQLModel):
    __tablename__ = '"Users"'

    name: str
    cpf: str
    birth_date: date
    address_id: int
    contact_id: int
    role_id: int
    registration_timestamp: datetime

    @property
    def formatted_cpf(self) -> str:
        cpf = ''.join(filter(str.isdigit, self.cpf))
        return f"{cpf[:3]}.***.***-{cpf[9:]}"
    

    def name_validator(self, value: str):
        if (not value) or (not isinstance(value, str)):
            raise ValueError("User 'name' must be a non empty string.")
        
    def cpf_validator(self, value: str):
        def is_valid_cpf(cpf: str) -> bool:
            cpf = ''.join(filter(str.isdigit, cpf))
            if len(cpf) != 11 or cpf == cpf[0] * 11:
                return False

            for i in range(9, 11):
                sum = 0
                for j in range(0, i):
                    sum += int(cpf[j]) * ((i + 1) - j)
                digit = (sum * 10) % 11
                if digit == 10:
                    digit = 0
                if digit != int(cpf[i]):
                    return False
            return True
        
        if (not value) or (not isinstance(value, str)) or (not is_valid_cpf(value)):
            raise ValueError("User 'cpf' must be a valid CPF.")
        
    def birth_date_validator(self, value: date):
        if (not isinstance(value, date)) or (value >= date.today()):
            raise ValueError("User 'birth_date' must be a valid date in the past.")
        
    def address_id_validator(self, value: int):
        if (not isinstance(value, int)) or (value <= 0):
            raise ValueError("User 'address_id' must be a positive integer.")
        
    def contact_id_validator(self, value: int):
        if (not isinstance(value, int)) or (value <= 0):
            raise ValueError("User 'contact_id' must be a positive integer.")
        
    def role_id_validator(self, value: int):
        if (not isinstance(value, int)) or (value <= 0):
            raise ValueError("User 'role_id' must be a positive integer.")
        
    def registration_timestamp_validator(self, value: datetime):
        value = normalize_datetime(value)

        if (not isinstance(value, datetime)) or (value > datetime.utcnow()):
            raise ValueError("User 'registration_timestamp' must be a valid datetime in the past.")


class UserRead(BaseModel):
    id: int
    name: str
    cpf: str
    birth_date: date
    address_id: int
    contact_id: int
    role_id: int
    registration_timestamp: datetime

    def __init__(self, user: User):
        super().__init__(
            id=user.id,
            name=user.name,
            cpf=user.formatted_cpf,  # CPF formatado automaticamente
            birth_date=user.birth_date,
            address_id=user.address_id,
            contact_id=user.contact_id,
            role_id=user.role_id,
            registration_timestamp=user.registration_timestamp
        )

class UserCreate(BaseModel):
    name: str
    cpf: str
    birth_date: date
    address_id: int
    contact_id: int
    role_id: int

class UserUpdate(BaseModel):
    name: Optional[str] = None
    cpf: Optional[str] = None
    birth_date: Optional[date] = None
    address_id: Optional[int] = None
    contact_id: Optional[int] = None

class UserRoleUpdate(BaseModel):
    role_id: int