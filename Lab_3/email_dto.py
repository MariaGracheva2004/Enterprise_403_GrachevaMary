# email_dto.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import json

@dataclass
class WelcomeEmailMessage:
    """DTO для сообщения о приветственном письме (аналог Java DTO)"""
    customer_id: int
    email: str
    first_name: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def __post_init__(self):
        if isinstance(self.created_at, datetime):
            self.created_at = self.created_at.isoformat()
    
    def to_json(self) -> str:
        """Сериализация в JSON"""
        return json.dumps({
            'customer_id': self.customer_id,
            'email': self.email,
            'first_name': self.first_name,
            'created_at': self.created_at
        })
    
    @classmethod
    def from_json(cls, json_str: str) -> 'WelcomeEmailMessage':
        """Десериализация из JSON"""
        data = json.loads(json_str)
        return cls(
            customer_id=data['customer_id'],
            email=data['email'],
            first_name=data['first_name'],
            created_at=data.get('created_at', datetime.now().isoformat())
        )
    
    def __str__(self) -> str:
        return f"WelcomeEmailMessage(customerId={self.customer_id}, email={self.email}, firstName={self.first_name}, createdAt={self.created_at})"