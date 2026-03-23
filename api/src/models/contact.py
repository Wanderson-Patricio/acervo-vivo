from ._base_class import BasePostgreSQLModel

class Contact(BasePostgreSQLModel):
    __tablename__ = '"Contacts"'

    email: str = None
    phone_number: str = None

    