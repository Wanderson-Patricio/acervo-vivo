from fastapi import HTTPException, Request, Depends
from typing import Dict, List
from pydantic import BaseModel

from ._base_router import BaseRouterModel, get_user_access_level, get_role_access_level
from ..models import Contact, ContactRead, ContactUpdate
from ..controllers import BaseController
from ..models import User, Role
from ..middlewares import get_current_user
from ..middlewares.require import require, RolesEnum
from ..errors import NotAuthorizedException, NotFoundException

contact_router_model = BaseRouterModel(Contact)

user_controller = BaseController(User)
role_controller = BaseController(Role)

@contact_router_model.router.get('/', response_model=List[ContactRead])
@require(RolesEnum.Analyst)
def list_contacts(
        request: Request,
        current_user: Dict = Depends(get_current_user)
    ) -> List[ContactRead]:

    query_params = dict(request.query_params)
    controller = contact_router_model.controller

    result = controller.list(**query_params)

    return [ContactRead(data) for data in result]


@contact_router_model.router.get('/{id:int}', response_model=ContactRead)
@require(RolesEnum.Viewer)
def get_contact(
    id: int,
    current_user: Dict = Depends(get_current_user)
) -> ContactRead:

    viewer_access_level = get_role_access_level(RolesEnum.Viewer, role_controller)
    user_access_level = get_user_access_level(current_user)

    if user_access_level == viewer_access_level:
        user_id = current_user.get("user_id")

        user = user_controller.get_by_id(user_id)
        if user and user.contact_id != id:
            raise NotAuthorizedException(detail=f"Access denied: {RolesEnum.Viewer} role can only view their own contact")

    controller = contact_router_model.controller
    data = controller.get_by_id(id)
    if not data:
        raise NotFoundException(Contact, id)
    return ContactRead(data)

    
class ContactUpdateResponse(BaseModel):
    message: str
    affected_rows: int

@contact_router_model.router.put('/{id:int}', response_model=ContactUpdateResponse)
@require(RolesEnum.Viewer)
def update_contact(
    id: int,
    updated_contact: ContactUpdate,
    current_user: Dict = Depends(get_current_user)
) -> ContactUpdateResponse:

    viewer_access_level = get_role_access_level(RolesEnum.Viewer, role_controller)
    user_access_level = get_user_access_level(current_user)

    if user_access_level == viewer_access_level:
        user_id = current_user.get("user_id")

        user = user_controller.get_by_id(user_id)
        if user and user.contact_id != id:
            raise NotAuthorizedException(detail=f"Access denied: {RolesEnum.Viewer} role can only update their own contact")

    controller = contact_router_model.controller
    try:
        update_data = updated_contact.dict(exclude_unset=True)
        rowcount = controller.update(id, **update_data)
        if rowcount == 0:
            raise NotFoundException(Contact, id)
        
        return ContactUpdateResponse(
            message=f'Contact of id {id} updated successfully',
            affected_rows=rowcount
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
class ContactDeleteResponse(BaseModel):
    message: str
    affected_rows: int

@contact_router_model.router.delete('/{id:int}', response_model=ContactDeleteResponse)
@require(RolesEnum.Viewer)
def delete_contact(
    id: int,
    current_user: Dict = Depends(get_current_user)
) -> ContactDeleteResponse:
    
    viewer_access_level = get_role_access_level(RolesEnum.Viewer, role_controller)
    user_access_level = get_user_access_level(current_user)

    if user_access_level == viewer_access_level:
        user_id = current_user.get("user_id")

        user = user_controller.get_by_id(user_id)
        if user and user.contact_id != id:
            raise NotAuthorizedException(detail=f"Access denied: {RolesEnum.Viewer} role can only delete their own contact")

    controller = contact_router_model.controller
    try:
        rowcount = controller.delete(id)
        if rowcount == 0:
            raise NotFoundException(Contact, id)
        
        return ContactDeleteResponse(
            message=f'Contact of id {id} deleted successfully',
            affected_rows=rowcount
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))