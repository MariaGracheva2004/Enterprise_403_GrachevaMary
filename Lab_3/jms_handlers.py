# jms_handlers.py
import logging
from email_consumer import handle_email_queue

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def handle_customer_created(message: dict):
    
    logger.info(f" Новый клиент создан!")
    customer = message.get('customer', {})
    logger.info(f"   ID: {customer.get('id')}")
    logger.info(f"   Имя: {customer.get('first_name')} {customer.get('last_name')}")
    logger.info(f"   Email: {customer.get('email')}")


def handle_customer_updated(message: dict):
    
    logger.info(f" Клиент обновлен!")
    customer = message.get('customer', {})
    logger.info(f"   ID: {customer.get('id')}")
    logger.info(f"   Имя: {customer.get('first_name')} {customer.get('last_name')}")
    logger.info(f"   Email: {customer.get('email')}")


def handle_customer_deleted(message: dict):
    
    logger.info(f" Клиент удален!")
    customer = message.get('customer', {})
    logger.info(f"   ID: {customer.get('id')}")
    logger.info(f"   Имя: {customer.get('first_name')} {customer.get('last_name')}")
    logger.info(f"   Email: {customer.get('email')}")


def handle_topic_events(message: dict):
    
    logger.info(f" Событие из топика: {message.get('eventType')} - {message.get('customer', {}).get('id')}")


# Сопоставление очередей с обработчиками
QUEUE_HANDLERS = {
    '/queue/customer.created.queue': handle_customer_created,
    '/queue/customer.updated.queue': handle_customer_updated,
    '/queue/customer.deleted.queue': handle_customer_deleted,
    '/queue/email.queue': handle_email_queue,
    '/topic/customer.events.topic': handle_topic_events,
}