from fastapi import HTTPException, Request, Depends
from typing import Any, Dict, List
from pydantic import BaseModel

from ._base_router import BaseRouterModel, AccessDeniedException, get_user_access_level
from ..models import Role, RoleCreate, RoleUpdate
from ..middlewares import get_current_user
from ..middlewares.require import require, RolesEnum

# Aqui está o "pulo do gato": injetamos a dependência no nível do Router.
# Agora, QUALQUER rota definida neste arquivo exigirá o header Authorization.
role_router_model = BaseRouterModel(Role)


@role_router_model.router.get('/', response_model=List[Role])
@require(role=RolesEnum.Viewer)
def list_roles(
        request: Request,
        current_user: Dict = Depends(get_current_user)
    ) -> List[Role]:

    query_params = dict(request.query_params)
    controller = role_router_model.controller
    result = controller.list(**query_params)
    user_access_level = get_user_access_level(current_user)
    result = [role for role in result if role.access_level <= user_access_level]

    return [data for data in result]

@role_router_model.router.get('/{id:int}', response_model=Role)
@require(role=RolesEnum.Viewer)
def get_by_id(
        id: int,
        current_user: Dict = Depends(get_current_user)
    ) -> Role:

    user_role = Role(**current_user.get("role"))

    if user_role.name == RolesEnum.Viewer and user_role.id != id:
        raise AccessDeniedException(RolesEnum.Viewer)

    controller = role_router_model.controller
    data = controller.get_by_id(id)
    if not data:
        raise HTTPException(status_code=404, detail='Item not found')
    return data


class RoleCreateResponse(BaseModel):
    message: str
    role: RoleCreate

@role_router_model.router.post('/', response_model=RoleCreateResponse)
@require(role=RolesEnum.Admin)
def create_role(
        new_role: RoleCreate,
        current_user: Dict = Depends(get_current_user)
    ) -> RoleCreateResponse:

    controller = role_router_model.controller
    try:
        # Corrigindo a criação da instância de Role
        new_role_instance = Role(**new_role.dict())
        controller.insert(new_role_instance)
        return RoleCreateResponse(
            message='Role created successfully',
            role=new_role
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

class RoleUpdateResponse(BaseModel):
    message: str
    affected_rows: int

@role_router_model.router.put('/{id:int}', response_model=RoleUpdateResponse)
@require(role=RolesEnum.Admin)
def update_role(
        id: int,
        updated_fields: RoleUpdate,
        current_user: Dict = Depends(get_current_user)
    ) -> RoleUpdateResponse:

    controller = role_router_model.controller
    try:
        # Usando exclude_unset para ignorar campos não enviados
        update_data = updated_fields.dict(exclude_unset=True)
        rowcount = controller.update(id, **update_data)
        if rowcount == 0:
            raise HTTPException(status_code=404, detail='Item not found')
        
        return RoleUpdateResponse(
            message=f'Role of id {id} updated successfully',
            affected_rows=rowcount
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

class RoleDeleteResponse(BaseModel):
    message: str
    affected_rows: int

@role_router_model.router.delete('/{id:int}', response_model=RoleDeleteResponse)
@require(role=RolesEnum.Admin)
def delete_role(
        id: int,
        current_user: Dict = Depends(get_current_user)
    ) -> RoleDeleteResponse:

    controller = role_router_model.controller
    rowcount = controller.delete(id)
    if rowcount == 0:
        raise HTTPException(status_code=404, detail='Item not found')
    
    return RoleDeleteResponse(
        message=f'Role of id {id} deleted successfully',
        affected_rows=rowcount
    )