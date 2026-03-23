from fastapi import HTTPException, Request, Depends
from typing import Any, Dict, List

from ._base_router import BaseRouterModel, DENIED_ACCESS_EXCEPTION, get_user_access_level, get_role_access_level
from ..models import Contact, ContactCreate, ContactUpdate
from ..controllers import BaseController
from ..models import User, Role
from ..middlewares import get_current_user
from ..middlewares.require import require, RolesEnum

contact_router_model = BaseRouterModel(Contact)

user_controller = BaseController(User)
role_controller = BaseController(Role)

@contact_router_model.router.get('/')
@require(RolesEnum.Viewer)
def list_contacts(
        request: Request,
        current_user: Dict = Depends(get_current_user)
    ) -> List[Dict]:

    query_params = dict(request.query_params)
    controller = contact_router_model.controller
    
    viewer_access_level = get_role_access_level(RolesEnum.Viewer, role_controller)
    user_access_level = get_user_access_level(current_user)

    if user_access_level == viewer_access_level:
        user_id = current_user.get("user_id")

        user = user_controller.get_by_id(user_id)
        if user and user.contact_id:
            contact_id = user.contact_id

        if query_params.get("id") and int(query_params["id"]) != contact_id:
            raise DENIED_ACCESS_EXCEPTION
        
        query_params["id"] = contact_id

    result = controller.list(**query_params)

    return [data.to_dict() for data in result]


@contact_router_model.router.get('/{id:int}')
@require(RolesEnum.Viewer)
def get_contact(
    id: int,
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:

    viewer_access_level = get_role_access_level(RolesEnum.Viewer, role_controller)
    user_access_level = get_user_access_level(current_user)

    if user_access_level == viewer_access_level:
        user_id = current_user.get("user_id")

        user = user_controller.get_by_id(user_id)
        if user and user.contact_id != id:
            raise DENIED_ACCESS_EXCEPTION

    controller = contact_router_model.controller
    data = controller.get_by_id(id)
    if not data:
        raise HTTPException(status_code=404, detail='Item not found')
    return data.to_dict()

@contact_router_model.router.post('/')
@require(RolesEnum.Viewer)
def create_contact(
    new_contact: ContactCreate,
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:

    controller = contact_router_model.controller
    try:
        # Corrigindo a criação da instância de Contact
        new_contact_instance = Contact(**new_contact.dict())
        controller.insert(new_contact_instance)
        return {
            'message': 'Contact created successfully',
            'new_contact': new_contact
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@contact_router_model.router.put('/{id:int}')
@require(RolesEnum.Viewer)
def update_contact(
    id: int,
    updated_contact: ContactUpdate,
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:

    viewer_access_level = get_role_access_level(RolesEnum.Viewer, role_controller)
    user_access_level = get_user_access_level(current_user)

    if user_access_level == viewer_access_level:
        user_id = current_user.get("user_id")

        user = user_controller.get_by_id(user_id)
        if user and user.contact_id != id:
            raise DENIED_ACCESS_EXCEPTION

    controller = contact_router_model.controller
    try:
        update_data = updated_contact.dict(exclude_unset=True)
        rowcount = controller.update(id, **update_data)
        if rowcount == 0:
            raise HTTPException(status_code=404, detail='Item not found')
        
        return {
            'message': f'Contact of id {id} updated successfully',
            'affected_rows': rowcount
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@contact_router_model.router.delete('/{id:int}')
@require(RolesEnum.Viewer)
def delete_contact(
    id: int,
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    
    viewer_access_level = get_role_access_level(RolesEnum.Viewer, role_controller)
    user_access_level = get_user_access_level(current_user)

    if user_access_level == viewer_access_level:
        user_id = current_user.get("user_id")

        user = user_controller.get_by_id(user_id)
        if user and user.contact_id != id:
            raise DENIED_ACCESS_EXCEPTION

    controller = contact_router_model.controller
    try:
        rowcount = controller.delete(id)
        if rowcount == 0:
            raise HTTPException(status_code=404, detail='Item not found')
        
        return {
            'message': f'Contact of id {id} deleted successfully',
            'affected_rows': rowcount
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))