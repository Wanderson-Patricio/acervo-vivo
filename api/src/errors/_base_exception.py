from typing import Optional
from fastapi import HTTPException, status

from ..models import BasePostgreSQLModel

class BaseException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


class BadRequestException(BaseException):
    def __init__(self, detail: Optional[str] = None):
        detail = "The request could not be understood or was missing required parameters." if detail is None else detail
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class NotAuthenticatedException(BaseException):
    def __init__(self, detail: Optional[str] = None):
        detail = "Authentication credentials were not provided or are invalid." if detail is None else detail
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class NotAuthorizedException(BaseException):
    def __init__(self, detail: Optional[str] = None):
        detail = "You do not have permission to perform this action." if detail is None else detail
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class NotFoundException(BaseException):
    def __init__(self, model: BasePostgreSQLModel, id: int):
        detail = f"{model.__name__} with ID {id} not found."
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


