from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base  

class Customer(Base):

    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True) 
    first_name = Column(String, nullable=False)        
    last_name = Column(String, nullable=False)         
    email = Column(String, unique=True, nullable=False) 
    created_at = Column(DateTime, default=datetime.utcnow) 