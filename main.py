from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session


from database import SessionLocal, engine, Base
import models
from repository import CustomerRepository
from service import CustomerService

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Customer Management System")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@app.post("/customers/")
def create_customer(first_name: str, last_name: str, email: str, db: Session = Depends(get_db)):
    repo = CustomerRepository(db)
    service = CustomerService(repo)
    try:
        return service.create_customer(first_name, last_name, email)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/customers/")
def read_customers(db: Session = Depends(get_db)):
    repo = CustomerRepository(db)
    service = CustomerService(repo)
    return service.list_customers()

@app.get("/customers/{customer_id}")
def read_customer(customer_id: int, db: Session = Depends(get_db)):
    repo = CustomerRepository(db)
    service = CustomerService(repo)
    customer = service.get_customer(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Клиент не найден")
    return customer

@app.delete("/customers/{customer_id}")
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    repo = CustomerRepository(db)
    service = CustomerService(repo)
    success = service.delete_customer(customer_id)
    if not success:
        raise HTTPException(status_code=404, detail="Клиент не найден")
    return {"message": "Клиент успешно удален"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)