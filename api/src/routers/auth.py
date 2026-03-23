from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..controllers import BaseController
from ..models import Authentication, Contact, User, Role
from ..utils import CriptDict
from ..middlewares import AuthJWT

class LoginRequest(BaseModel):
    email: str
    password: str

auth_router = APIRouter(prefix='/auth', tags=['Auth'])
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

@auth_router.post('/login')
def login(request: LoginRequest):
    # 1. Busca o usuário
    user = get_user_by_email(request.email)
    if not user:
        raise INVALID_AUTH_EXC

    # 2. Valida as credenciais
    if not verify_user_credentials(user.id, request.password):
        raise INVALID_AUTH_EXC
    
    # 3. Busca permissões (Role)
    

    # 4. Gera o Token
    token = AuthJWT.create_access_token({
        'user_id': user.id
    })

    return {'message': 'Login successful', 'access_token': token}