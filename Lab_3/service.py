# service.py
from repository import CustomerRepository, UserRepository
from models import Customer, User
import security
from cache_config import customers_cache, all_customers_cache, cache_evict
from cachetools import cached
from jms_producer import get_jms_producer
from email_producer import get_email_producer
import json

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
        result = self.repository.create(new_customer)
        
        
        try:
            producer = get_jms_producer()
            customer_data = {
                'id': result.id,
                'first_name': result.first_name,
                'last_name': result.last_name,
                'email': result.email,
                'created_at': str(result.created_at)
            }
            producer.send_customer_event('CREATED', customer_data)
            print(f"JMS: Отправлено событие CREATED для клиента {result.id}")
        except Exception as e:
            print(f"JMS: Ошибка отправки - {e}")
        
        # ОТПРАВКА ПРИВЕТСТВЕННОГО EMAIL (через отдельную очередь)
        try:
            email_producer = get_email_producer()
            email_producer.send_welcome_email(result.id, result.email, result.first_name)
            print(f"JMS: Отправлено сообщение для приветственного письма на {result.email}")
        except Exception as e:
            print(f"JMS: Ошибка отправки email сообщения - {e}")
        
        return result

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
        
        result = self.repository.update(customer)
        
        
        try:
            producer = get_jms_producer()
            customer_data = {
                'id': result.id,
                'first_name': result.first_name,
                'last_name': result.last_name,
                'email': result.email
            }
            producer.send_customer_event('UPDATED', customer_data)
            print(f"JMS: Отправлено событие UPDATED для клиента {result.id}")
        except Exception as e:
            print(f"JMS: Ошибка отправки - {e}")
        
        return result

    @cache_evict("customers", "allCustomers")
    def delete_customer(self, customer_id: int):
        customer = self.repository.get_by_id(customer_id)
        if customer:
            customer_data = {
                'id': customer.id,
                'first_name': customer.first_name,
                'last_name': customer.last_name,
                'email': customer.email
            }
            self.repository.delete(customer)
            
            
            try:
                producer = get_jms_producer()
                producer.send_customer_event('DELETED', customer_data)
                print(f"JMS: Отправлено событие DELETED для клиента {customer_id}")
            except Exception as e:
                print(f"JMS: Ошибка отправки - {e}")
            
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