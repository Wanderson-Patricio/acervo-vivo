from datetime import datetime
from fastapi import Depends
from typing import Dict
from pydantic import BaseModel
from base64 import b64decode

from ._base_router import BaseRouterModel
from ..models import Authentication, AuthenticationUpdate
from ..middlewares import get_current_user
from ..middlewares.require import require, RolesEnum
from ..utils import CriptDict
from ..errors import NotAuthenticatedException, NotAuthorizedException, NotFoundException

authentication_router_model = BaseRouterModel(Authentication)

class AuthenticationUpdateResponse(BaseModel):
    message: str
    affected_rows: int

@authentication_router_model.router.put('/', response_model=AuthenticationUpdateResponse)
@require(RolesEnum.Viewer)
def update_authentication(
        updated_authentication: AuthenticationUpdate,
        current_user: Dict = Depends(get_current_user)
    ) -> AuthenticationUpdateResponse:

    if updated_authentication.user_id != current_user.get("user_id"):
        raise NotAuthorizedException(detail=f"Access denied: users can only update their own authentication")

    controller = authentication_router_model.controller

    update_data = updated_authentication.dict(exclude_unset=True)

    password = update_data.pop("password")
    update_data["hash_password"] = CriptDict.hash_password(password)
    update_data["last_time_altered"] = datetime.utcnow()
    update_data["is_blocked"] = False # Desbloqueia a conta ao alterar a senha
    update_data["failed_attempts"] = 0 # Reseta as tentativas falhas ao alterar a senha
        
    rowcount = controller.update(updated_authentication.user_id, **update_data)

    if rowcount == 0:
        raise NotFoundException(Authentication, updated_authentication.user_id)
    
    return AuthenticationUpdateResponse(message=f"Authentication updated successfully", affected_rows=rowcount)


class AuthenticationDeleteResponse(BaseModel):
    message: str
    affected_rows: int

@authentication_router_model.router.delete('/', response_model=AuthenticationDeleteResponse)
@require(RolesEnum.Admin)
def delete_authentication(
        id: int,
        current_user: Dict = Depends(get_current_user)
    ) -> AuthenticationDeleteResponse:

    controller = authentication_router_model.controller

    rowcount = controller.delete(id)

    if rowcount == 0:
        raise NotFoundException(Authentication, id)
    
    return AuthenticationDeleteResponse(
        message=f"Authentication of id {id} deleted successfully", 
        affected_rows=rowcount
    )


class AuthenticationBlockResponse(BaseModel):
    message: str
