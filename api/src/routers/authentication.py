from datetime import datetime
from fastapi import HTTPException, Request, Depends
from typing import Any, Dict, List
from pydantic import BaseModel, ValidationError
from base64 import b64decode

from ._base_router import BaseRouterModel, AccessDeniedException
from ..models import Authentication, AuthenticationCreate, AuthenticationUpdate
from ..middlewares import get_current_user
from ..middlewares.require import require, RolesEnum
from ..utils import CriptDict

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
        raise AccessDeniedException(RolesEnum.Viewer)

    controller = authentication_router_model.controller

    update_data = updated_authentication.dict(exclude_unset=True)

    # Tratar atualização de senha
    if "password_bytes" in update_data:
        try:
            password = b64decode(update_data.pop("password_bytes")).decode('utf-8')
            print(password, end='\n' * 10)
            update_data["hash_password"] = CriptDict.hash_password(password)
        except (AttributeError, UnicodeDecodeError):
            raise HTTPException(status_code=400, detail="Invalid binary password format.")

    rowcount = controller.update(updated_authentication.user_id, **update_data)

    if rowcount == 0:
        raise HTTPException(status_code=404, detail="Authentication not found.")
    
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
        raise HTTPException(status_code=404, detail="Authentication not found.")
    
    return AuthenticationDeleteResponse(
        message=f"Authentication of id {id} deleted successfully", 
        affected_rows=rowcount
    )