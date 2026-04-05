from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

class CustomerNotFoundException(Exception):
    def __init__(self, customer_id: int):
        self.customer_id = customer_id
        self.message = f"Клиент с ID {customer_id} не найден"
        super().__init__(self.message)

class AccessDeniedException(Exception):
    def __init__(self, required_roles: list):
        self.required_roles = required_roles
        self.message = f"Доступ запрещен. Требуемые роли: {required_roles}"
        super().__init__(self.message)

def register_exception_handlers(app: FastAPI):
    
    @app.exception_handler(CustomerNotFoundException)
    async def customer_not_found_handler(request: Request, exc: CustomerNotFoundException):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "timestamp": str(datetime.now()),
                "status": 404,
                "error": "Not Found",
                "message": exc.message,
                "path": str(request.url)
            }
        )
    
    @app.exception_handler(AccessDeniedException)
    async def access_denied_handler(request: Request, exc: AccessDeniedException):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "timestamp": str(datetime.now()),
                "status": 403,
                "error": "Forbidden",
                "message": exc.message,
                "path": str(request.url)
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "timestamp": str(datetime.now()),
                "status": 400,
                "error": "Bad Request",
                "message": "Ошибка валидации данных",
                "details": exc.errors(),
                "path": str(request.url)
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "timestamp": str(datetime.now()),
                "status": 500,
                "error": "Internal Server Error",
                "message": "Внутренняя ошибка сервера",
                "path": str(request.url)
            }
        )