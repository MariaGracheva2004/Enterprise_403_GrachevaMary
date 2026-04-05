# email_consumer.py
# EmailNotificationConsumer
# Обрабатывает сообщения из очереди email.queue и отправляет письма

import logging
import time
import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailService:
   
    
    def __init__(self):
        
        self.smtp_config = {
            'enabled': False,  
            'host': 'smtp.gmail.com',
            'port': 587,
            'username': 'your_email@gmail.com',
            'password': 'your_password'
        }
    
    def send_welcome_email(self, to_email: str, first_name: str, customer_id: int) -> bool:
        
        subject = f"Добро пожаловать в наш сервис, {first_name}!"
        
        body = f"""
Уважаемый(ая) {first_name}!

Спасибо за регистрацию в нашем сервисе. Ваш аккаунт успешно создан.

ID вашего аккаунта: {customer_id}
Email: {to_email}

Мы рады приветствовать вас в нашей системе управления клиентами!

Если у вас возникнут вопросы, пожалуйста, свяжитесь с нашей службой поддержки.

С уважением,
Команда поддержки Customer Management System
"""
        
        if self.smtp_config['enabled']:
            return self._send_via_smtp(to_email, subject, body)
        else:
            logger.info(f"[ИМИТАЦИЯ] Приветственное письмо отправлено на адрес: {to_email}")
            logger.info(f"   Тема: {subject}")
            logger.info(f"   Получатель: {first_name}")
            return True
    
    def _send_via_smtp(self, to_email: str, subject: str, body: str) -> bool:
        """Реальная отправка через SMTP"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_config['username']
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(self.smtp_config['host'], self.smtp_config['port']) as server:
                server.starttls()
                server.login(self.smtp_config['username'], self.smtp_config['password'])
                server.send_message(msg)
            
            logger.info(f" Реальное письмо отправлено на {to_email}")
            return True
            
        except Exception as e:
            logger.error(f" Ошибка отправки реального письма: {e}")
            return False


class EmailNotificationConsumer:
   
    
    def __init__(self):
        self.email_service = EmailService()
        self._running = False
    
    def receive_welcome_email(self, message: Dict[str, Any]) -> bool:
        
        logger.info(f" Получено сообщение для отправки email: {message}")
        
        
        try:
            
            message_type = message.get('messageType', 'welcome-email')
            customer_id = message.get('customerId')
            email = message.get('email')
            first_name = message.get('firstName', 'Клиент')
            created_at = message.get('createdAt')
            
            logger.info(f"   Тип сообщения: {message_type}")
            logger.info(f"   ID клиента: {customer_id}")
            logger.info(f"   Email получателя: {email}")
            logger.info(f"   Имя получателя: {first_name}")
            logger.info(f"   Время создания: {created_at}")
            
            
            logger.info(" Отправка email... (имитация долгой операции 2 секунды)")
            time.sleep(2)  
            logger.info(" 2 секунды прошло, продолжаем...")
            
            
            success = self.email_service.send_welcome_email(
                to_email=email,
                first_name=first_name,
                customer_id=customer_id
            )
            
            if success:
                logger.info(f" Email успешно обработан для клиента ID: {customer_id}")
                logger.info(f"   Получатель: {email}")
            else:
                logger.error(f" Не удалось отправить email для клиента ID: {customer_id}")
                
                raise Exception(f"Failed to send email for customer {customer_id}")
            
            
            return success
            
        except Exception as e:
            logger.error(f" Ошибка при отправке email: {e}")
            
            raise e
    
    def process_message_with_retry(self, message: Dict[str, Any], max_retries: int = 3):
        
        for attempt in range(max_retries):
            try:
                return self.receive_welcome_email(message)
            except Exception as e:
                logger.warning(f" Попытка {attempt + 1}/{max_retries} не удалась: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)  # Ждём перед повторной попыткой
                else:
                    logger.error(f" Все {max_retries} попыток не удались для сообщения {message}")
                    raise



def handle_email_queue(message: Dict[str, Any]):
  
    consumer = EmailNotificationConsumer()
    consumer.process_message_with_retry(message)