import re
from typing import Optional
from pydantic import BaseModel

from ._base_class import BasePostgreSQLModel

class Contact(BasePostgreSQLModel):
    __tablename__ = '"Contacts"'

    email: str = None
    phone_number: str = None

    @property
    def formatted_phone_number(self) -> str:
        if self.phone_number:
            digits = re.sub(r'\D', '', self.phone_number)
            if len(digits) == 11:
                return f"+{digits[0]} ({digits[1:4]}) {digits[4:9]}-{digits[9:]}"
            elif len(digits) == 10:
                return f"+{digits[0]} ({digits[1:3]}) {digits[3:7]}-{digits[7:]}"
            elif len(digits) == 12:
                return f"+{digits[0:2]} ({digits[2:4]}) {digits[4:9]}-{digits[9:]}"
            elif len(digits) == 13:
                return f"+{digits[0:2]} ({digits[2:4]}) {digits[4:9]}-{digits[9:]}"
        return self.phone_number


    def email_validator(self, value: str) -> None:
        if value and not re.match(r'^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$', value):
            raise ValueError('Invalid email address')

    def phone_number_validator(self, value: str) -> str:
        if value:
            # Remove todos os caracteres não numéricos
            digits = re.sub(r'\D', '', value)
            # Verifica se o número possui o formato correto (12 ou 13 dígitos)
            if not re.match(r'^\d{12,13}$', digits):
                raise ValueError('Phone number be in the format: +<country_code> (DDD) XXXXX-XXXX or XXXXXXXXXXXX')
        else:
            raise ValueError('Phone number is required.')


class ContactRead(BaseModel):
    id: int
    email: Optional[str] = None
    phone_number: Optional[str] = None

    def __init__(self, contact: Contact):
        super().__init__(
            id=contact.id,
            email=contact.email,
            phone_number=contact.formatted_phone_number
        )

class ContactCreate(BaseModel):
    email: str
    phone_number: str


class ContactUpdate(BaseModel):
    email: Optional[str] = None
    phone_number: Optional[str] = None