from base64 import b64decode

from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime, date

from ..models import UserCreate, ContactCreate, AddressCreate, AuthenticationCreate
from ..models import User, Contact, Address, Authentication
from ..controllers import BaseController
from ..models import Role
from ..middlewares.require import RolesEnum
from ..utils import CriptDict
from ..errors import NotAuthenticatedException, NotFoundException, BadRequestException

registration_router = APIRouter(prefix="/registration", tags=["Registration"])


class UserCreateNonContactAddress(BaseModel):
    name: str
    cpf: str
    birth_date: date

class UserCreateRequest(BaseModel):
    user: UserCreateNonContactAddress
    contact: ContactCreate
    address: AddressCreate
    password: str


class UserCreateResponse(BaseModel):
    message: str
    user_name: str
    user_id: int

def register_contact(contact_data: ContactCreate) -> int:
    
    contact_controller = BaseController(Contact)
    contact = Contact(
        phone_number=contact_data.phone_number,
        email=contact_data.email
    )

    return contact_controller.insert(contact)

def register_address(address_data: AddressCreate) -> int:
    
    address_controller = BaseController(Address)
    address = Address(
        street=address_data.street,
        number=address_data.number,
        complement=address_data.complement,
        neighbourhood=address_data.neighbourhood,
        city=address_data.city,
        state=address_data.state,
        country=address_data.country,
        zip_code=address_data.zip_code
    )

    return address_controller.insert(address)


def verify_user_exists(cpf: str, user_controller: BaseController) -> bool:
    existing_users = user_controller.list(cpf=cpf)
    return len(existing_users) > 0

def register_user_in_db(
        user_data: UserCreate,
        contact_id: int,
        address_id: int
    ) -> UserCreateResponse:

    user_controller = BaseController(User)
    role_controller = BaseController(Role)

    role_id = role_controller.list(name=RolesEnum.Viewer)[0].id

    user = User(
        name=user_data.name,
        cpf=user_data.cpf,
        birth_date=user_data.birth_date,
        address_id=address_id,
        contact_id=contact_id,
        role_id=role_id,
        registration_timestamp=datetime.now()
    )

    return user_controller.insert(user)


def register_authentication(
        authentication_data: AuthenticationCreate,
    ) -> None:

    authentication_controller = BaseController(Authentication)

    password = authentication_data.password

    authentication = Authentication(
        user_id=authentication_data.user_id,
        hash_password=CriptDict.hash_password(password),
        last_time_altered=datetime.utcnow(),
        is_blocked=False
    )

    authentication_controller.insert(authentication)


@registration_router.post('/', response_model=UserCreateResponse)
def register_user(
        registration_data: UserCreateRequest
    ) -> UserCreateResponse:

    if verify_user_exists(registration_data.user.cpf, BaseController(User)):
        raise BadRequestException(detail="User with this CPF already exists.")

    # Criar contato
    contact_id = register_contact(registration_data.contact)

    # Criar endereço
    address_id = register_address(registration_data.address)

    user_id = register_user_in_db(registration_data.user, contact_id, address_id)

    register_authentication(
        AuthenticationCreate(
            user_id=user_id,
            password=registration_data.password
        )
    )

    return UserCreateResponse(
        message=f"User registered successfully.",
        user_name=registration_data.user.name,
        user_id=user_id
    )