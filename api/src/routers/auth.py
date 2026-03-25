from base64 import b64decode

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..controllers import BaseController
from ..models import Authentication, Contact, User, Role
from ..utils import CriptDict
from ..middlewares import AuthJWT


auth_router = APIRouter(prefix='/authentication', tags=['Authentication'])
INVALID_AUTH_EXC = HTTPException(status_code=401, detail='Email ou senha inválidos')

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
    password_bytes: bytes

class AuthLoginResponse(BaseModel):
    message: str
    access_token: str

@auth_router.post('/login', response_model=AuthLoginResponse)
def login(request: LoginRequest) -> AuthLoginResponse:
    # 1. Busca o usuário
    user = get_user_by_email(request.email)
    if not user:
        raise INVALID_AUTH_EXC

    # 2. Valida as credenciais
    try:
        password = b64decode(request.password_bytes).decode('utf-8')
    except (AttributeError, UnicodeDecodeError):
        raise INVALID_AUTH_EXC

    if not verify_user_credentials(user.id, password):
        raise INVALID_AUTH_EXC
    
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