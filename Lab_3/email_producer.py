# email_producer.py
# Аналог NotificationProducer в Spring Boot

import logging
from typing import Optional
from jms_producer import get_jms_producer
from email_dto import WelcomeEmailMessage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailNotificationProducer:
  
    
    def __init__(self):
        self.producer = None
        self.email_queue = "/queue/email.queue"
    
    def _get_producer(self):
        
        if self.producer is None:
            self.producer = get_jms_producer()
        return self.producer
    
    def send_welcome_email(self, customer_id: int, email: str, first_name: str) -> bool:
      
        # Создаем DTO сообщение
        message = WelcomeEmailMessage(
            customer_id=customer_id,
            email=email,
            first_name=first_name
        )
        
        logger.info(f" Отправка сообщения в очередь {self.email_queue}: {message}")
        
        
        message_data = {
            'messageType': 'welcome-email',  
            'customerId': customer_id,
            'email': email,
            'firstName': first_name,
            'createdAt': message.created_at
        }
        
        # Отправляем в JMS очередь
        try:
            producer = self._get_producer()
            result = producer.send_message(
                destination=self.email_queue,
                message=message_data,
                persistent=True
            )
            
            if result:
                logger.info(f" Сообщение для {email} отправлено в очередь (асинхронно)")
            else:
                logger.error(f" Не удалось отправить сообщение для {email}")
            
            return result
            
        except Exception as e:
            logger.error(f" Ошибка при отправке сообщения в очередь: {e}")
            return False


# Глобальный экземпляр 
_email_producer = None

def get_email_producer() -> EmailNotificationProducer:
    """Получить экземпляр EmailNotificationProducer (синглтон)"""
    global _email_producer
    if _email_producer is None:
        _email_producer = EmailNotificationProducer()
    return _email_producer