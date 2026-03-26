from fastapi import HTTPException, Request, Depends
from typing import Dict, List
from pydantic import BaseModel

from ._base_router import BaseRouterModel, get_user_access_level, get_role_access_level
from ..models import Address, AddressRead, AddressUpdate
from ..controllers import BaseController
from ..models import User, Role
from ..middlewares import get_current_user
from ..middlewares.require import require, RolesEnum
from ..errors import NotFoundException, NotAuthorizedException

address_router_model = BaseRouterModel(Address)

user_controller = BaseController(User)
role_controller = BaseController(Role)

@address_router_model.router.get('/', response_model=List[AddressRead])
@require(RolesEnum.Analyst)
def list_addresses(
        request: Request,
        current_user: Dict = Depends(get_current_user)
    ) -> List[AddressRead]:

    query_params = dict(request.query_params)
    controller = address_router_model.controller

    result = controller.list(**query_params)

    return [AddressRead(data) for data in result]


@address_router_model.router.get('/{id:int}', response_model=AddressRead)
@require(RolesEnum.Viewer)
def get_address(
    id: int,
    current_user: Dict = Depends(get_current_user)
) -> AddressRead:

    viewer_access_level = get_role_access_level(RolesEnum.Viewer, role_controller)
    user_access_level = get_user_access_level(current_user)

    if user_access_level == viewer_access_level:
        user_id = current_user.get("user_id")

        user = user_controller.get_by_id(user_id)
        if user and user.address_id != id:
            raise NotAuthorizedException(detail=f"Access denied: {RolesEnum.Viewer} role can only view their own address")

    controller = address_router_model.controller
    data = controller.get_by_id(id)
    if not data:
        raise NotFoundException()
    return AddressRead(data)

    
class AddressUpdateResponse(BaseModel):
    message: str
    affected_rows: int

@address_router_model.router.put('/{id:int}', response_model=AddressUpdateResponse)
@require(RolesEnum.Viewer)
def update_Address(
    id: int,
    updated_Address: AddressUpdate,
    current_user: Dict = Depends(get_current_user)
) -> AddressUpdateResponse:

    viewer_access_level = get_role_access_level(RolesEnum.Viewer, role_controller)
    user_access_level = get_user_access_level(current_user)

    if user_access_level == viewer_access_level:
        user_id = current_user.get("user_id")

        user = user_controller.get_by_id(user_id)
        if user and user.address_id != id:
            raise NotAuthorizedException(detail=f"Access denied: {RolesEnum.Viewer} role can only update their own address")

    controller = address_router_model.controller
    try:
        update_data = updated_Address.dict(exclude_unset=True)
        rowcount = controller.update(id, **update_data)
        if rowcount == 0:
            raise NotFoundException()
        
        return AddressUpdateResponse(
            message=f'Address of id {id} updated successfully',
            affected_rows=rowcount
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
class AddressDeleteResponse(BaseModel):
    message: str
    affected_rows: int

@address_router_model.router.delete('/{id:int}', response_model=AddressDeleteResponse)
@require(RolesEnum.Admin)
def delete_Address(
    id: int,
    current_user: Dict = Depends(get_current_user)
) -> AddressDeleteResponse:

    controller = address_router_model.controller
    try:
        rowcount = controller.delete(id)
        if rowcount == 0:
            raise NotFoundException()
        
        return AddressDeleteResponse(
            message=f'Address of id {id} deleted successfully',
            affected_rows=rowcount
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))