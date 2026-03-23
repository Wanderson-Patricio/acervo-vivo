from pydantic import BaseModel, ValidationError
from typing import Any, Callable, ClassVar, List, Optional


class Validator:
    def __init__(self, instance, attr: str, func: Callable[[Any], None]):
        self.instance = instance
        self.attr = attr
        self.func = func

    def execute(self):
        value = getattr(self.instance, self.attr, None)
        try:
            self.func(value)
        except Exception as e:
            raise ValueError(f"Validation failed for attribute '{self.attr}': {str(e)}") from e


class BasePostgreSQLModel(BaseModel):
    __tablename__: str
    id: Optional[int] = None

    model_config = {
        'arbitrary_types_allowed': True  # Permitir tipos arbitrários como Validator
    }

    def __init__(self, *args, **kwargs):
        if args:
            fields = list(self.model_fields.keys())
            kwargs.update({field: value for field, value in zip(fields, args)})
        super().__init__(**kwargs)
        self.__validator_list__: List[Validator] = []
        self.validate()

    def to_dict(self) -> dict:
        fields = list(self.model_fields.keys())
        return {field: getattr(self, field) for field in fields}

    def add_validator(self,attr: str, func: Callable[[Any], None]):
        self.__validator_list__.append(Validator(self, attr, func))

    def validate(self):
        for field in self.model_fields:
            validator_func = getattr(self, f"{field}_validator", None)
            if callable(validator_func):
                self.add_validator(field, validator_func)

        for validator in getattr(self, '__validator_list__', []):
            validator.execute()

        del self.__validator_list__

    def id_validator(self, value):
        if value is not None and (not isinstance(value, int) or value < 0):
            raise ValueError(f"ID must be a non-negative integer or None. given {value} instead.")