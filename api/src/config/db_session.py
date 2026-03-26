from typing import Any, Optional, List, Callable
from dataclasses import dataclass

from .db import DatabaseConfig, BASE_CONFIG, DatabaseContextManager
from ..models import BasePostgreSQLModel

class NotFilteredQueryException(Exception):
    pass


@dataclass
class SessionOptions:
    model_attributes: List[str]
    filters: List[str]
    order_by: Optional[str] = None
    limit: Optional[int] = None
    offset: Optional[int] = None
    method: Optional[str] = None
    parameters: List = None
    get_all: Optional[bool] = None
    to_model: Optional[bool] = False
    update_set_clauses: List[str] = None


@dataclass
class QueryClauses:
    filters: List[str]
    order_by: Optional[str] = None
    limit: Optional[int] = None
    offset: Optional[int] = None


class Helpers:
    @staticmethod
    def only(method: str = 'SELECT'):
        def only_implementation(func: Callable):
            def wrapper(self, *args, **kwargs):
                if self.options.method != method:
                    raise ValueError(f"The method '{func.__name__}' can only be used with {method} queries.")
                return func(self, *args, **kwargs)
            return wrapper
        return only_implementation


class PostgreSQLSession:
    def __init__(self, model: BasePostgreSQLModel, config: Optional[DatabaseConfig] = None):
        self.config = config if config else BASE_CONFIG
        self.model = model
        self.options = SessionOptions(
            model_attributes=list(self.model.model_fields.keys()),
            filters=[],
            parameters=[],
            update_set_clauses=[]
        )

    def reset_options(self):
        self.options.filters = []
        self.options.order_by = None
        self.options.limit = None
        self.options.offset = None
        self.options.method = None
        self.options.parameters = []
        self.options.get_all = None
        self.options.to_model = False
        self.options.update_set_clauses = []

    def select(self):
        self.options.method = "SELECT"
        return self

    def insert(self, model_instance: Optional[BasePostgreSQLModel] = None):
        self.options.method = "INSERT"
        if model_instance:
            self.options.parameters = [
                getattr(model_instance, attr)
                for attr in self.options.model_attributes
                if attr != "id"
            ]
        return self

    def delete(self):
        self.options.method = "DELETE"
        return self

    def update(self):
        self.options.method = "UPDATE"
        return self
    
    @Helpers.only("UPDATE")
    def set(self, **kwargs):
        if kwargs:
            for key, value in kwargs.items():
                if key not in self.options.model_attributes:
                    raise AttributeError(f"Attribute '{key}' is not valid for model '{self.model.__name__}'")
                self.options.parameters.append(value)
                self.options.update_set_clauses.append(key)
        return self

    def filter(self, **kwargs):
        if self.options.method == "UPDATE" and (not self.options.parameters):
            raise ValueError("When on update method, the setters must be passed before the filters.")
        
        for key in kwargs.keys():
            if key not in self.options.model_attributes:
                raise AttributeError(f"Attribute '{key}' is not valid for model '{self.model.__name__}'")
        self.options.filters.extend(kwargs.keys())
        self.options.parameters.extend(kwargs.values())
        return self

    @Helpers.only("SELECT")
    def order_by(self, field_name: str):
        if field_name not in self.model.model_attributes:
            raise AttributeError(f"Attribute '{field_name}' is not valid for model '{self.model.__name__}'")
        self.options.order_by = field_name
        return self

    @Helpers.only("SELECT")
    def limit(self, limit: int):
        if not isinstance(limit, int):
            raise ValueError("Limit must be an integer.")
        self.options.limit = limit
        return self

    @Helpers.only("SELECT")
    def offset(self, offset: int):
        if not isinstance(offset, int):
            raise ValueError("Offset must be an integer.")
        self.options.offset = offset
        return self
    
    @Helpers.only("SELECT")
    def all(self):
        self.options.get_all = True
        return self

    @Helpers.only("SELECT")
    def first(self):
        self.options.get_all = False
        self.options.limit = 1
        return self

    @Helpers.only("SELECT")
    def to_model(self):
        self.options.to_model = True
        return self

    def execute(self):
        with DatabaseContextManager(self.config) as conn:
            query_builder = QueryBuilder(self)
            executor = QueryExecutor(conn, query_builder)
            return executor.execute()

class QueryBuilder:
    def __init__(self, session: PostgreSQLSession):
        self.session = session

    def generate_clauses(self, clauses: QueryClauses):
        parts = []
        if clauses.filters:
            parts.append("WHERE " + " AND ".join(f"{k}=%s" for k in clauses.filters))
        if clauses.order_by:
            parts.append(f"ORDER BY {clauses.order_by}")
        if clauses.limit is not None:
            parts.append(f"LIMIT {clauses.limit}")
        if clauses.offset is not None:
            parts.append(f"OFFSET {clauses.offset}")
        return " ".join(parts)
    
    def build(self):
        build_map = {
            "SELECT": self.build_select,
            "INSERT": self.build_insert,
            "UPDATE": self.build_update,
            "DELETE": self.build_delete,
        }
        return build_map[self.session.options.method]()

    def build_select(self):
        options = self.session.options
        if not options.model_attributes:
            raise ValueError("Model must have at least one attribute to build a SELECT query.")
        if options.get_all is None:
            raise ValueError("Must specify .all() or .first() before executing a SELECT query.")
        if not options.get_all:
            options.limit = 1
        return f"SELECT {', '.join(options.model_attributes)} FROM {self.session.model.__tablename__} {self.generate_clauses(options)};"

    def build_insert(self):
        attributes = [attr for attr in self.session.options.model_attributes if attr != "id"]
        return f"INSERT INTO {self.session.model.__tablename__} ({', '.join(attributes)}) VALUES ({', '.join(['%s'] * len(attributes))});"

    def build_update(self):
        if self.session.options.limit is not None or self.session.options.offset is not None:
            raise ValueError("UPDATE queries cannot have LIMIT or OFFSET.")

        if not self.session.options.filters:
            raise NotFilteredQueryException("UPDATE queries must have at least one filter.")

        # Gera a cláusula SET apenas para os atributos presentes nos parâmetros
        set_clause = ", ".join(
            f"{attr}=%s" for attr in self.session.options.update_set_clauses
        )

        return f"UPDATE {self.session.model.__tablename__} SET {set_clause} {self.generate_clauses(self.session.options)};"

    def build_delete(self):
        if not self.session.options.filters:
            raise NotFilteredQueryException("DELETE queries must have at least one filter.")
        return f"DELETE FROM {self.session.model.__tablename__} {self.generate_clauses(self.session.options)};"

class QueryExecutor:
    def __init__(self, conn, query_builder: QueryBuilder):
        self.conn = conn
        self.query_builder = query_builder

    def execute(self):
        query = self.query_builder.build()
        options = self.query_builder.session.options
        parameters = options.parameters

        # Certifica-se de que os parâmetros estão alinhados com os placeholders e são do tipo correto
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, tuple(parameters))
        except Exception as e:
            raise ValueError(f"Erro ao executar a consulta: {query} com parâmetros: {options.parameters}. Detalhes: {e}")

        if options.method == "SELECT":
            if options.get_all is None:
                raise ValueError("Must specify .all() or .first() before executing a SELECT query.")
            
            result = cursor.fetchall()
            if options.to_model:
                result = [self.query_builder.session.model(*row) for row in result]
            return result[0] if not options.get_all and result else result

        self.conn.commit()

        if options.method in ["INSERT"]:
            # Retorna o ID do modelo inserido ou atualizado
            cursor.execute("SELECT LASTVAL();")
            return cursor.fetchone()[0]

        return cursor.rowcount
