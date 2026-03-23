from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .verify_credentials import AuthJWT
from ..controllers import BaseController
from ..models import Role

# O parâmetro auto_error=True (padrão) garante que o FastAPI 
# bloqueie a requisição se o header "Authorization" estiver faltando.
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials # Extrai apenas a string do token
    try:
        payload = AuthJWT.verify_token(token)
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token inválido: user_id ausente")
        
        role = BaseController(Role).get_by_id(user_id)

        return {
            'user_id': user_id,
            'role': role.to_dict() if role else None
        }
    except ValueError as e:
        detail = "Token expirado" if "expirado" in str(e) else "Token inválido"
        raise HTTPException(status_code=401, detail=detail)