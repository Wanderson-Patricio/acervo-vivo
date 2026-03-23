from fastapi import Depends, HTTPException
from functools import wraps
from enum import StrEnum

from ..middlewares import get_current_user
from ..routers import BaseRouterModel
from ..models import Role

class RolesEnum(StrEnum):
    Admin = "Admin"
    Editor = "Editor"
    Analyst = "Analyst"
    Viewer = "Viewer"


def require(role: RolesEnum):
    """
    Decorator de permissão.
    Exemplo: @require(role="Admin")
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args ,current_user = Depends(get_current_user), **kwargs):
            # Obtém nível mínimo da role exigida
            role_router_model = BaseRouterModel(Role)
            controller = role_router_model.controller
            role_object = controller.list(name=role)[0]
            required_level = int(role_object.access_level)

            # Nível atual do usuário
            user_level = int(current_user.get("role", {}).get("access_level", 0))

            if user_level < required_level:
                raise HTTPException(
                    status_code=403,
                    detail=f"Acesso negado. Papel '{role}' exigido."
                )

            # Continua para a rota original
            return func(*args, current_user=current_user, **kwargs)

        return wrapper
    return decorator