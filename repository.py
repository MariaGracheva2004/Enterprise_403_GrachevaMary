from sqlalchemy.orm import Session
from models import Customer  

class CustomerRepository:
    def __init__(self, db: Session):
        self.db = db  

    def get_all(self):
        return self.db.query(Customer).all()

    def get_by_id(self, customer_id: int):
        return self.db.query(Customer).filter(Customer.id == customer_id).first()

    def create(self, customer: Customer):
        self.db.add(customer)      
        self.db.commit()           
        self.db.refresh(customer)  
        return customer

    def delete(self, customer: Customer):
        self.db.delete(customer)
        self.db.commit()