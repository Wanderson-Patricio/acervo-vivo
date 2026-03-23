from typing import List

from ..config import PostgreSQLSession
from ..models import BasePostgreSQLModel

class BaseController:
    def __init__(self, model: BasePostgreSQLModel):
        self.db_session = PostgreSQLSession(model)


    def list(self, **filters) -> List[BasePostgreSQLModel]:
        lim = int(filters.pop('limit', 10))
        page = int(filters.pop('page', 1))
        offset = (page - 1) * lim
        return self.db_session.select().all().filter(**filters).limit(lim).offset(offset).to_model().execute()
        
    
    def get_by_id(self, id: int) -> BasePostgreSQLModel:
        return self.db_session.select().filter(id=id).first().to_model().execute()
        
    
    def insert(self, model_instance: BasePostgreSQLModel) -> int:
        return self.db_session.insert(model_instance).execute()
        
    
    def update(self, id: int, **setters) -> int:
        return self.db_session.update().set(**setters).filter(id=id).execute()
        
    
    def delete(self, id: int) -> int:
        return self.db_session.delete().filter(id=id).execute()