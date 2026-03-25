from fastapi import HTTPException, Request, Depends
from typing import Dict, List
from pydantic import BaseModel
from datetime import datetime

from ._base_router import BaseRouterModel, DENIED_ACCESS_EXCEPTION, get_user_access_level, get_role_access_level
from ..models import User, UserRead, UserCreate, UserUpdate
from ..controllers import BaseController
from ..models import Role
from ..middlewares import get_current_user
from ..middlewares.require import require, RolesEnum

# Aqui está o "pulo do gato": injetamos a dependência no nível do Router.
# Agora, QUALQUER rota definida neste arquivo exigirá o header Authorization.
user_router_model = BaseRouterModel(User)
role_controller = BaseController(Role)


@user_router_model.router.get('/', response_model=List[UserRead])
@require(role=RolesEnum.Analyst)
def list_users(
        request: Request,
        current_user: Dict = Depends(get_current_user)
    ) -> List[UserRead]:

    query_params = dict(request.query_params)
    controller = user_router_model.controller

    result = controller.list(**query_params)

    return [UserRead(result_item) for result_item in result]


@user_router_model.router.get('/{user_id:int}', response_model=UserRead)
@require(role=RolesEnum.Viewer)
def get_user_by_id(
        user_id: int,
        current_user: Dict = Depends(get_current_user)
    ) -> UserRead:

    viewer_access_level = get_role_access_level(RolesEnum.Viewer, role_controller)
    user_access_level = get_user_access_level(current_user)

    if user_access_level == viewer_access_level and user_id != current_user.get("user_id"):
        raise DENIED_ACCESS_EXCEPTION

    controller = user_router_model.controller
    result = controller.get_by_id(user_id)

    if not result:
        raise HTTPException(status_code=404, detail="User not found.")
    
    return UserRead(result)


class UserCreateResponse(BaseModel):
    message: str
    user: UserCreate

@user_router_model.router.post('/', response_model=UserCreateResponse)
@require(role=RolesEnum.Admin)
def create_user(
        user_data: UserCreate
    ) -> UserCreateResponse:

    controller = user_router_model.controller
    user = User(
        name=user_data.name,
        cpf=user_data.cpf,
        birth_date=user_data.birth_date,
        address_id=user_data.address_id,
        contact_id=user_data.contact_id,
        role_id=user_data.role_id,
        registration_timestamp=datetime.now()
    )

    try:
        controller.insert(user)

        return UserCreateResponse(
            message="User created successfully.",
            user=user_data
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

class UserUpdateResponse(BaseModel):
    message: str
    user: UserUpdate

@user_router_model.router.put('/{user_id:int}', response_model=UserUpdateResponse)
@require(role=RolesEnum.Viewer)
def update_user(
        user_id: int,
        user_data: UserUpdate,
        current_user: Dict = Depends(get_current_user)
    ) -> UserUpdateResponse:

    viewer_access_level = get_role_access_level(RolesEnum.Viewer, role_controller)
    user_access_level = get_user_access_level(current_user)

    if user_access_level == viewer_access_level and user_id != current_user.get("user_id"):
        raise DENIED_ACCESS_EXCEPTION

    controller = user_router_model.controller
    affected_rows = controller.update(user_id, **user_data.dict())

    if affected_rows == 0:
        raise HTTPException(status_code=404, detail="User not found.")
    
    return UserUpdateResponse(
        message="User updated successfully.",
        user=user_data
    )
    

class UserDeleteResponse(BaseModel):
    message: str
    affected_rows: int

@user_router_model.router.delete('/{id:int}', response_model=UserDeleteResponse)
@require(role=RolesEnum.Admin)
def delete_user(
        id: int,
        current_user = Depends(get_current_user)
    ) -> UserDeleteResponse:

    controller = user_router_model.controller
    affected_rows = controller.delete(id)

    if affected_rows == 0:
        raise HTTPException(status_code=404, detail="User not found.")
    
    return UserDeleteResponse(
        message="User deleted successfully.",
        affected_rows=affected_rows
    )