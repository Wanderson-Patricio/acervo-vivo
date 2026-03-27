from fastapi import FastAPI, APIRouter
from pydantic import BaseModel
import uvicorn
import os
from dotenv import load_dotenv
from typing import Dict, Union

load_dotenv(".env", override=True)

from src.routers import (
    role_router_model,
    contact_router_model,
    address_router_model,
    authentication_router_model,
    user_router_model,
    auth_router,
    registration_router
)


tags_metadata = [
        {
            "name": "Authentication",
            "description": "Endpoints relacionados à autenticação de usuários."
        },
        {
            "name": "Registration",
            "description": "Endpoints relacionados ao registro de novos usuários."
        },
        {
            "name": "Roles",
            "description": "Endpoints relacionados a papéis de usuário."
        },
        {
            "name": "Users",
            "description": "Endpoints relacionados a usuários."
        },
        {
            "name": "Contacts",
            "description": "Endpoints relacionados a contatos de usuários."
        },
        {
            "name": "Addresses",
            "description": "Endpoints relacionados a endereços de usuários."
        }
]

app = FastAPI(
    title="Acervo Vivo API",
    description="API para gerenciar o acervo vivo, incluindo usuários, papéis e permissões.",
    version="1.0.0",
    contact={
        "name": ":Wanderson Faustino Patricio",
        "email": "wanderfapat@gmail.com"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=tags_metadata
)

routers_to_include: list[APIRouter] = [
    role_router_model.router,
    contact_router_model.router,
    address_router_model.router,
    authentication_router_model.router,
    user_router_model.router,
    auth_router,
    registration_router
]

for rout in routers_to_include:
    app.include_router(rout)


class ProjectInfo(BaseModel):
    class Contact(BaseModel):
        name: str
        email: str

    title: str
    maintainer: Contact
    documentation_url: str
    description: str

@app.get('/', tags=['Root'], response_model=ProjectInfo)
def project_info() -> ProjectInfo:
    return ProjectInfo(
        title=app.title,
        maintainer=ProjectInfo.Contact(**app.contact),
        documentation_url=f"http://{os.environ.get('API_HOST')}:{os.environ.get('API_PORT')}/docs",
        description=app.description
    )


def main() -> None:
    host: str = os.environ.get('API_HOST')
    port: int = int(os.environ.get('API_PORT'))
    uvicorn.run('app:app', host=host, port=port, reload=True)


if __name__ == '__main__':
    main()
