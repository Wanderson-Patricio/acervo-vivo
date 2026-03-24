from fastapi import HTTPException, Request, Depends
from typing import Any, Dict, List
from pydantic import BaseModel

from ._base_router import BaseRouterModel, DENIED_ACCESS_EXCEPTION, get_user_access_level, get_role_access_level
from ..models import Address, AddressRead, AddressCreate, AddressUpdate
from ..controllers import BaseController
from ..models import User, Role
from ..middlewares import get_current_user
from ..middlewares.require import require, RolesEnum

address_router_model = BaseRouterModel(Address)

user_controller = BaseController(User)
role_controller = BaseController(Role)

@address_router_model.router.get('/', response_model=List[AddressRead])
@require(RolesEnum.Viewer)
def list_addresses(
        request: Request,
        current_user: Dict = Depends(get_current_user)
    ) -> List[AddressRead]:

    query_params = dict(request.query_params)
    controller = address_router_model.controller
    
    viewer_access_level = get_role_access_level(RolesEnum.Viewer, role_controller)
    user_access_level = get_user_access_level(current_user)

    if user_access_level == viewer_access_level:
        user_id = current_user.get("user_id")

        user = user_controller.get_by_id(user_id)
        if user and user.address_id:
            address_id = user.address_id

        if query_params.get("id") and int(query_params["id"]) != address_id:
            raise DENIED_ACCESS_EXCEPTION
        
        query_params["id"] = address_id

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
            raise DENIED_ACCESS_EXCEPTION

    controller = address_router_model.controller
    data = controller.get_by_id(id)
    if not data:
        raise HTTPException(status_code=404, detail='Item not found')
    return AddressRead(data)

class AddressCreateResponse(BaseModel):
    message: str
    address: AddressCreate

@address_router_model.router.post('/', response_model=AddressCreateResponse)
@require(RolesEnum.Admin)
def create_Address(
    new_Address: AddressCreate,
    current_user: Dict = Depends(get_current_user)
) -> AddressCreateResponse:

    controller = address_router_model.controller
    try:
        # Corrigindo a criação da instância de Address
        new_Address_instance = Address(**new_Address.dict())
        controller.insert(new_Address_instance)
        return AddressCreateResponse(
            message='Address created successfully',
            address=new_Address
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
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
            raise DENIED_ACCESS_EXCEPTION

    controller = address_router_model.controller
    try:
        update_data = updated_Address.dict(exclude_unset=True)
        rowcount = controller.update(id, **update_data)
        if rowcount == 0:
            raise HTTPException(status_code=404, detail='Item not found')
        
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
@require(RolesEnum.Viewer)
def delete_Address(
    id: int,
    current_user: Dict = Depends(get_current_user)
) -> AddressDeleteResponse:
    
    viewer_access_level = get_role_access_level(RolesEnum.Viewer, role_controller)
    user_access_level = get_user_access_level(current_user)

    if user_access_level == viewer_access_level:
        user_id = current_user.get("user_id")

        user = user_controller.get_by_id(user_id)
        if user and user.address_id != id:
            raise DENIED_ACCESS_EXCEPTION

    controller = address_router_model.controller
    try:
        rowcount = controller.delete(id)
        if rowcount == 0:
            raise HTTPException(status_code=404, detail='Item not found')
        
        return AddressDeleteResponse(
            message=f'Address of id {id} deleted successfully',
            affected_rows=rowcount
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))