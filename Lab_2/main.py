from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import models
import repository
import service
import auth_router
from database import SessionLocal, engine
from exceptions import register_exception_handlers, CustomerNotFoundException, AccessDeniedException


models.Base.metadata.create_all(bind=engine)


security_scheme = HTTPBearer()

app = FastAPI(
    title="Customer Management System v2",
    description="Система с JWT-авторизацией и разграничением ролей (RBAC)",
    version="2.0.0",
    swagger_ui_parameters={"persistAuthorization": True}
)


register_exception_handlers(app)


app.include_router(auth_router.router, prefix="/api/auth", tags=["Security"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user_with_roles(required_roles: list[str]):
    def role_checker(token: HTTPAuthorizationCredentials = Depends(security_scheme), db: Session = Depends(get_db)):
        
        user = auth_router.get_current_user(token.credentials, db)
        
        
        user_roles = [r.name for r in user.roles]
        
        
        for role in required_roles:
            if role in user_roles:
                return user
        
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Доступ запрещен. Требуемые роли: {required_roles}"
        )
    return role_checker




@app.get("/api/v1/customers/", tags=["Customers"])
def read_customers(
    page: int = 0,
    size: int = 10,
    sort_by: str = "id",
    sort_order: str = "asc",
    first_name: str = None,
    last_name: str = None,
    email: str = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_with_roles(["ROLE_USER", "ROLE_ADMIN"]))
):
    repo = repository.CustomerRepository(db)
    serv = service.CustomerService(repo)
    
    
    if first_name or last_name or email:
        result = serv.get_customers_with_filters(
            page=page, size=size, sort_by=sort_by, sort_order=sort_order,
            first_name=first_name, last_name=last_name, email=email
        )
    else:
        result = serv.list_customers(page=page, size=size, sort_by=sort_by, sort_order=sort_order)
    
    
    return {
        "content": result["items"],
        "pageable": {
            "page_number": result["page"],
            "page_size": result["size"],
            "sort": {"sorted": sort_by, "order": sort_order}
        },
        "total_elements": result["total"],
        "total_pages": result["pages"],
        "last": result["page"] >= result["pages"] - 1,
        "first": result["page"] == 0,
        "empty": len(result["items"]) == 0
    }


@app.get("/api/v1/customers/{customer_id}", tags=["Customers"])
def read_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_with_roles(["ROLE_USER", "ROLE_ADMIN"]))
):
    repo = repository.CustomerRepository(db)
    serv = service.CustomerService(repo)
    customer = serv.get_customer(customer_id)
    if not customer:
        raise CustomerNotFoundException(customer_id)
    return customer


@app.post("/api/v1/customers/", tags=["Customers"])
def create_customer(
    first_name: str, 
    last_name: str, 
    email: str, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_with_roles(["ROLE_ADMIN"]))
):
    repo = repository.CustomerRepository(db)
    serv = service.CustomerService(repo)
    return serv.create_customer(first_name, last_name, email)


@app.put("/api/v1/customers/{customer_id}", tags=["Customers"])
def update_customer(
    customer_id: int,
    first_name: str = None,
    last_name: str = None,
    email: str = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_with_roles(["ROLE_ADMIN"]))
):
    repo = repository.CustomerRepository(db)
    serv = service.CustomerService(repo)
    updated = serv.update_customer(customer_id, first_name, last_name, email)
    if updated:
        return updated
    raise CustomerNotFoundException(customer_id)


@app.delete("/api/v1/customers/{customer_id}", tags=["Customers"])
def delete_customer(
    customer_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_with_roles(["ROLE_ADMIN"]))
):
    repo = repository.CustomerRepository(db)
    serv = service.CustomerService(repo)
    if serv.delete_customer(customer_id):
        return {"message": "Customer deleted successfully"}
    raise CustomerNotFoundException(customer_id)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)