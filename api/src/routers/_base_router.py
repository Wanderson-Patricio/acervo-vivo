from typing import Dict

from fastapi import APIRouter, HTTPException

from ..controllers import BaseController
from ..models import BasePostgreSQLModel

class BaseRouterModel:
    def __init__(self, model: BasePostgreSQLModel):
        self.model = model
        self.prefix = model.__tablename__.lower().replace("\"", "")
        self.tags = [model.__tablename__.replace("\"", "")]
        self.router = self.get_router()

    @property
    def controller(self) -> BaseController:
        return BaseController(self.model)

    def get_router(self) -> APIRouter:
        router = APIRouter(
            prefix=f'/{self.prefix}', 
            tags=self.tags
        )

        return router
    

DENIED_ACCESS_EXCEPTION = HTTPException(status_code=403, detail='Acesso negado: nível de acesso insuficiente.')


def get_user_access_level(current_user: Dict) -> int:
    """Função auxiliar para obter o nível de acesso do usuário atual."""
    role_info = current_user.get('role', {})
    return int(role_info.get('access_level', 0))

def get_role_access_level(role_name: str, controller: BaseController) -> int:
    """Função auxiliar para obter o nível de acesso de um papel específico."""
    role = controller.list(name=role_name)
    if role:
        return int(role[0].access_level)
    return 0