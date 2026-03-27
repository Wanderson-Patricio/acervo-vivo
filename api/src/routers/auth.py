from base64 import b64decode

from fastapi import APIRouter
from pydantic import BaseModel
from ..controllers import BaseController
from ..models import Authentication, Contact, User, Role
from ..utils import CriptDict
from ..middlewares import AuthJWT
from ..errors import NotAuthenticatedException


auth_router = APIRouter(prefix='/authentication', tags=['Authentication'])
INVALID_AUTH_EXC = NotAuthenticatedException(detail='Email ou senha inválidos')

MAXIMUM_RETRIES = 5

# --- Funções Auxiliares ---

def get_user_by_email(email: str):
    """Encapsula a busca em cascata: Contact -> User."""
    contact = BaseController(Contact).list(email=email)
    if not contact:
        return None
    
    users = BaseController(User).list(contact_id=contact[0].id)
    return users[0] if users else None

def verify_user_credentials(user_id: int, password: str) -> bool:
    """Valida se a senha informada bate com o hash no banco."""
    auth_records = BaseController(Authentication).list(user_id=user_id)
    if not auth_records:
        return False
    
    return CriptDict.verify_password(password, auth_records[0].hash_password)

# --- Endpoint Principal ---

class LoginRequest(BaseModel):
    email: str
    password: str

class AuthLoginResponse(BaseModel):
    message: str
    access_token: str

@auth_router.post('/login', response_model=AuthLoginResponse)
def login(request: LoginRequest) -> AuthLoginResponse:
    # 1. Busca o usuário
    user = get_user_by_email(request.email)
    if not user:
        raise INVALID_AUTH_EXC

    password = request.password

    auth_controller = BaseController(Authentication)
    auth_records = auth_controller.list(user_id=user.id)[0]
    auth_controller.db_session.reset_options()

    if auth_records.is_blocked:
        raise NotAuthenticatedException(detail="Account is blocked due to multiple failed login attempts. Please contact support.")

    if not verify_user_credentials(user.id, password):
        update_data = {"failed_attempts": auth_records.failed_attempts + 1}
        if auth_records.failed_attempts >= MAXIMUM_RETRIES - 1:
            update_data["is_blocked"] = True

        print(auth_controller.db_session.options, end='\n' * 10)
        auth_controller.update(auth_records.id, **update_data)
        auth_controller.db_session.reset_options()

        remaining_attempts = MAXIMUM_RETRIES - auth_records.failed_attempts - 1

        if remaining_attempts <= 0:
            detail = "Account is blocked due to multiple failed login attempts. Please contact support."
        else:
            detail = f"Invalid credentials. {remaining_attempts} {'attempts' if remaining_attempts > 1 else 'attempt'} remaining before account is blocked."

        raise NotAuthenticatedException(detail=detail)
    
    auth_controller.update(auth_records.id, failed_attempts=0, is_blocked=False)
    role = BaseController(Role).get_by_id(user.role_id)

    # 4. Gera o Token
    token = AuthJWT.create_access_token({
        'user_id': user.id,
        'role': role.to_dict() if role else None
    })

    return AuthLoginResponse(
        message=f"Login successful for user '{user.name}'",
        access_token=token
    )