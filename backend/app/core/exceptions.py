"""
Custom API Exceptions
"""
from typing import Optional, Any, Dict
from fastapi import HTTPException, status


class APIException(HTTPException):
    """Base API exception"""

    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class NotFoundException(APIException):
    """Resource not found exception"""

    def __init__(self, resource: str = "Resource", resource_id: Optional[str] = None):
        detail = f"{resource} non trouve"
        if resource_id:
            detail = f"{resource} avec ID '{resource_id}' non trouve"
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class UnauthorizedException(APIException):
    """Unauthorized access exception"""

    def __init__(self, detail: str = "Non autorise"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class ForbiddenException(APIException):
    """Forbidden access exception"""

    def __init__(self, detail: str = "Acces interdit"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class BadRequestException(APIException):
    """Bad request exception"""

    def __init__(self, detail: str = "Requete invalide"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class ConflictException(APIException):
    """Conflict exception (e.g., duplicate resource)"""

    def __init__(self, detail: str = "Conflit - ressource existe deja"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class ValidationException(APIException):
    """Validation error exception"""

    def __init__(self, detail: str = "Erreur de validation", errors: Optional[list] = None):
        message = detail
        if errors:
            message = f"{detail}: {', '.join(errors)}"
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=message)


class ServiceUnavailableException(APIException):
    """Service unavailable exception"""

    def __init__(self, service: str = "Service"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"{service} temporairement indisponible"
        )
