from fastapi import Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .verify_credentials import AuthJWT
from ..errors import NotAuthenticatedException

# O parâmetro auto_error=True (padrão) garante que o FastAPI 
# bloqueie a requisição se o header "Authorization" estiver faltando.
class CustomHTTPBearer(HTTPBearer):
    def make_not_authenticated_error(self):
        # Sobrescreve o método para usar a mensagem personalizada
        raise NotAuthenticatedException()


security = CustomHTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    try:
        payload = AuthJWT.verify_token(token)
        return payload
    except ValueError as e:
        raise NotAuthenticatedException()