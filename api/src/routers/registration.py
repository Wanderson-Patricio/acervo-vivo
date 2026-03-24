from fastapi import APIRouter, HTTPException, Request, Depends
from typing import Dict, List
from pydantic import BaseModel
from datetime import datetime

from ._base_router import BaseRouterModel, DENIED_ACCESS_EXCEPTION, get_user_access_level, get_role_access_level
from ..models import UserCreate, ContactCreate, AddressCreate
from ..models import User, Contact, Address
from ..controllers import BaseController
from ..models import Role
from ..middlewares import get_current_user
from ..middlewares.require import require, RolesEnum

registration_router = APIRouter(prefix="/registration", tags=["Registration"])


class UserCreateRequest(BaseModel):
    user: UserCreate
    contact: ContactCreate
    address: AddressCreate

class UserCreateResponse(BaseModel):
    message: str
    user: UserCreateRequest

@registration_router.post('/', response_model=UserCreateResponse)
def register_user(
        registration_data: UserCreateRequest
    ) -> UserCreateResponse:

    user_controller = BaseController(User)
    contact_controller = BaseController(Contact)
    address_controller = BaseController(Address)
    role_controller = BaseController(Role)

    # Criar contato
    contact = Contact(
        phone_number=registration_data.contact.phone_number,
        email=registration_data.contact.email
    )

    contact_id = contact_controller.insert(contact)

    # Criar endereço
    address = Address(
        street=registration_data.address.street,
        number=registration_data.address.number,
        complement=registration_data.address.complement,
        neighbourhood=registration_data.address.neighbourhood,
        city=registration_data.address.city,
        state=registration_data.address.state,
        country=registration_data.address.country,
        zip_code=registration_data.address.zip_code
    )
    address_id = address_controller.insert(address)

    role_id = role_controller.list(name=RolesEnum.Viewer)[0].id

    user = User(
        name=registration_data.user.name,
        cpf=registration_data.user.cpf,
        birth_date=registration_data.user.birth_date,
        address_id=address_id,
        contact_id=contact_id,
        role_id=role_id,
        registration_timestamp=datetime.now()
    )

    user_controller.insert(user)

    return UserCreateResponse(
        message=f"User registered successfully.{contact_id=}, {address_id=}",
        user=registration_data
    )