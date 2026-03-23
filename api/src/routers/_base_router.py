from fastapi import APIRouter

from ..controllers import BaseController
from ..models import BasePostgreSQLModel

class BaseRouterModel:
    def __init__(self, model: BasePostgreSQLModel):
        self.model = model
        self.prefix = model.__tablename__.lower().replace("\"", "")
        self.tags = [model.__tablename__.replace("\"", "")]
        self.router = self.get_router()

    @property
    def controller(self) -> BaseController:
        return BaseController(self.model)

    def get_router(self) -> APIRouter:
        router = APIRouter(
            prefix=f'/{self.prefix}', 
            tags=self.tags
        )

        return router