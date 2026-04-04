from repository import CustomerRepository
from models import Customer

class CustomerService:
    def __init__(self, repository: CustomerRepository):
        self.repository = repository

    def list_customers(self):
        return self.repository.get_all()

    def get_customer(self, customer_id: int):
        return self.repository.get_by_id(customer_id)

    def create_customer(self, first_name: str, last_name: str, email: str):

        if "@" not in email:
            raise ValueError("Некорректный адрес почты!")
            
        new_customer = Customer(first_name=first_name, last_name=last_name, email=email)
        return self.repository.create(new_customer)

    def delete_customer(self, customer_id: int):
        customer = self.repository.get_by_id(customer_id)
        if customer:
            self.repository.delete(customer)
            return True
        return False