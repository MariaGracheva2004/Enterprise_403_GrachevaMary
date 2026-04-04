from repository import CustomerRepository, UserRepository
from models import Customer, User
import security
from cache_config import customers_cache, all_customers_cache, cache_evict
from cachetools import cached

class CustomerService:
    def __init__(self, repository: CustomerRepository):
        self.repository = repository

    def list_customers(self, page: int = 0, size: int = 10, sort_by: str = "id", sort_order: str = "asc"):
        
        skip = page * size
        return self.repository.get_all(skip=skip, limit=size, sort_by=sort_by, sort_order=sort_order)

    def get_customers_with_filters(self, page: int = 0, size: int = 10, sort_by: str = "id", 
                                    sort_order: str = "asc", first_name: str = None, 
                                    last_name: str = None, email: str = None):
        
        skip = page * size
        return self.repository.get_all_with_filters(
            skip=skip, limit=size, sort_by=sort_by, sort_order=sort_order,
            first_name=first_name, last_name=last_name, email=email
        )

    @cached(customers_cache)
    def get_customer(self, customer_id: int):
        
        print(f"ЗАГРУЗКА КЛИЕНТА {customer_id} ИЗ БАЗЫ ДАННЫХ")
        return self.repository.get_by_id(customer_id)

    @cache_evict("customers", "allCustomers")
    def create_customer(self, first_name: str, last_name: str, email: str):
        
        if "@" not in email:
            raise ValueError("Некорректный адрес почты!")
            
        new_customer = Customer(first_name=first_name, last_name=last_name, email=email)
        return self.repository.create(new_customer)

    @cache_evict("customers", "allCustomers")
    def update_customer(self, customer_id: int, first_name: str = None, last_name: str = None, email: str = None):
        
        customer = self.repository.get_by_id(customer_id)
        if not customer:
            return None
        
        if first_name:
            customer.first_name = first_name
        if last_name:
            customer.last_name = last_name
        if email:
            if "@" not in email:
                raise ValueError("Некорректный адрес почты!")
            customer.email = email
            
        return self.repository.update(customer)

    @cache_evict("customers", "allCustomers")
    def delete_customer(self, customer_id: int):
        
        customer = self.repository.get_by_id(customer_id)
        if customer:
            self.repository.delete(customer)
            return True
        return False


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def register_user(self, username, password):
        hashed = security.hash_password(password)
        new_user = User(username=username, hashed_password=hashed)
        
        
        default_role = self.repository.get_role_by_name("ROLE_USER")
        if default_role:
            new_user.roles.append(default_role)
            
        return self.repository.create_user(new_user)