from typing import Optional
from pydantic import BaseModel


from ._base_class import BasePostgreSQLModel


class Address(BasePostgreSQLModel):
    __tablename__ = '"Addresses"'

    street: str
    number: int
    complement: Optional[str] = None
    neighbourhood: str
    city: str
    state: str
    country: str
    zip_code: Optional[str] = None

    def street_validator(self, value: str) -> None:
        if not value or len(value.strip()) == 0 or len(value) > 255:
            raise ValueError('Street is required and must be between 1 and 255 characters.')
    
    def number_validator(self, value: int) -> None:
        if value <= 0:
            raise ValueError('Number must be a positive integer.')
        
    def complement_validator(self, value: str) -> None:
        if value and len(value) > 255:
            raise ValueError('Complement must be at most 255 characters.')
        
    def neighbourhood_validator(self, value: str) -> None:
        if not value or len(value.strip()) == 0 or len(value) > 255:
            raise ValueError('Neighbourhood is required and must be between 1 and 255 characters.')
        
    def city_validator(self, value: str) -> None:
        if not value or len(value.strip()) == 0 or len(value) > 50:
            raise ValueError('City is required and must be between 1 and 50 characters.')

    def state_validator(self, value: str) -> None:
        if not value or len(value.strip()) == 0 or len(value) != 2 or not value.isupper():
            raise ValueError('State is required and must be a 2-character code full uppercase.')

    def country_validator(self, value: str) -> None:
        if not value or len(value.strip()) == 0 or len(value) > 50:
            raise ValueError('Country is required and must be between 1 and 50 characters.')
        
    def zip_code_validator(self, value: str) -> None:
        if value and (len(value) != 8 or not value.replace('-', '').isdigit()):
            raise ValueError('Zip code must be 8 characters long and contain only digits.')

    @property    
    def formatted_zip_code(self) -> Optional[str]:
        if self.zip_code and len(self.zip_code) == 8:
            return f"{self.zip_code[:5]}-{self.zip_code[5:]}"
        return self.zip_code
    
    def to_dict(self):
        return {
            "id": self.id,
            "street": self.street,
            "number": self.number,
            "complement": self.complement,
            "neighbourhood": self.neighbourhood,
            "city": self.city,
            "state": self.state,
            "country": self.country,
            "zip_code": self.formatted_zip_code
        }



class AddressCreate(BaseModel):
    street: str
    number: int
    complement: Optional[str] = None
    neighbourhood: str
    city: str
    state: str
    country: str
    zip_code: Optional[str] = None

class AddressUpdate(BaseModel):
    street: Optional[str] = None
    number: Optional[int] = None
    complement: Optional[str] = None
    neighbourhood: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    zip_code: Optional[str] = None