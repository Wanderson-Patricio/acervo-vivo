from ._base_class import BasePostgreSQLModel
from typing import Optional

class Address(BasePostgreSQLModel):
    __tablename__ = '"Addresses"'

    street: Optional[str] = None
    number: Optional[int] = None
    complement: Optional[str] = None
    neighbourhood: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    zip_code: Optional[str] = None