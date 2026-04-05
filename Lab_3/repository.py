from sqlalchemy.orm import Session
from models import Customer, User, Role
from sqlalchemy import asc, desc

class CustomerRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 10, sort_by: str = "id", sort_order: str = "asc"):
        query = self.db.query(Customer)
        
        # Сортировка
        sort_column = getattr(Customer, sort_by, Customer.id)
        if sort_order.lower() == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
        
        # Пагинация
        total = query.count()
        customers = query.offset(skip).limit(limit).all()
        
        return {
            "items": customers,
            "total": total,
            "page": skip // limit if limit > 0 else 0,
            "size": limit,
            "pages": (total + limit - 1) // limit if limit > 0 else 0
        }

    def get_all_with_filters(self, skip: int = 0, limit: int = 10, sort_by: str = "id", sort_order: str = "asc", first_name: str = None, last_name: str = None, email: str = None):
        query = self.db.query(Customer)
        
        # Фильтрация (динамические запросы)
        if first_name:
            query = query.filter(Customer.first_name.ilike(f"%{first_name}%"))
        if last_name:
            query = query.filter(Customer.last_name.ilike(f"%{last_name}%"))
        if email:
            query = query.filter(Customer.email.ilike(f"%{email}%"))
        
        # Сортировка
        sort_column = getattr(Customer, sort_by, Customer.id)
        if sort_order.lower() == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
        
        # Пагинация
        total = query.count()
        customers = query.offset(skip).limit(limit).all()
        
        return {
            "items": customers,
            "total": total,
            "page": skip // limit if limit > 0 else 0,
            "size": limit,
            "pages": (total + limit - 1) // limit if limit > 0 else 0
        }

    def get_by_id(self, customer_id: int):
        return self.db.query(Customer).filter(Customer.id == customer_id).first()

    def create(self, customer: Customer):
        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)
        return customer

    def update(self, customer: Customer):
        self.db.commit()
        self.db.refresh(customer)
        return customer

    def delete(self, customer: Customer):
        self.db.delete(customer)
        self.db.commit()


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_username(self, username: str):
        return self.db.query(User).filter(User.username == username).first()

    def create_user(self, user: User):
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_role_by_name(self, name: str):
        return self.db.query(Role).filter(Role.name == name).first()