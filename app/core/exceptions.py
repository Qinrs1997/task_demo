from fastapi import HTTPException, status


class NotFoundError(HTTPException):
    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message,
        )


class AuthenticationError(HTTPException):
    def __init__(self, message: str = "Authentication failed") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message,
        )
