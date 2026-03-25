from fastapi import HTTPException, Request, Depends
from typing import Any, Dict, List
from pydantic import BaseModel

from ._base_router import BaseRouterModel, AccessDeniedException, get_user_access_level, get_role_access_level
from ..models import Contact, ContactRead, ContactCreate, ContactUpdate
from ..controllers import BaseController
from ..models import User, Role
from ..middlewares import get_current_user
from ..middlewares.require import require, RolesEnum

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
            raise AccessDeniedException(RolesEnum.Viewer)

    controller = contact_router_model.controller
    data = controller.get_by_id(id)
    if not data:
        raise HTTPException(status_code=404, detail='Item not found')
    return ContactRead(data)

class ContactCreateResponse(BaseModel):
    message: str
    contact: ContactCreate

@contact_router_model.router.post('/', response_model=ContactCreateResponse)
@require(RolesEnum.Admin)
def create_contact(
    new_contact: ContactCreate,
    current_user: Dict = Depends(get_current_user)
) -> ContactCreateResponse:

    controller = contact_router_model.controller
    try:
        # Corrigindo a criação da instância de Contact
        new_contact_instance = Contact(**new_contact.dict())
        controller.insert(new_contact_instance)
        return ContactCreateResponse(
            message='Contact created successfully',
            contact=new_contact
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
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
            raise AccessDeniedException(RolesEnum.Viewer)

    controller = contact_router_model.controller
    try:
        update_data = updated_contact.dict(exclude_unset=True)
        rowcount = controller.update(id, **update_data)
        if rowcount == 0:
            raise HTTPException(status_code=404, detail='Item not found')
        
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
            raise AccessDeniedException(RolesEnum.Viewer)

    controller = contact_router_model.controller
    try:
        rowcount = controller.delete(id)
        if rowcount == 0:
            raise HTTPException(status_code=404, detail='Item not found')
        
        return ContactDeleteResponse(
            message=f'Contact of id {id} deleted successfully',
            affected_rows=rowcount
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))