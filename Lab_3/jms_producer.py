# jms_producer.py
# Отправка сообщений в ActiveMQ Artemis через STOMP

import stomp
import json
import logging
from datetime import datetime
from typing import Dict, Any
from jms_config import JMS_CONFIG, QUEUE_NAMES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JMSProducer:
    """Класс для отправки JMS сообщений в Artemis"""
    
    def __init__(self):
        self.conn = None
        self._connect()
    
    def _connect(self):
        """Установка соединения с брокером"""
        try:
            self.conn = stomp.Connection(
                host_and_ports=[(JMS_CONFIG['host'], JMS_CONFIG['port'])]
            )
            self.conn.connect(
                login=JMS_CONFIG['login'],
                passcode=JMS_CONFIG['passcode'],
                wait=True
            )
            logger.info("JMS Producer: Успешно подключен к ActiveMQ Artemis")
        except Exception as e:
            logger.error(f"JMS Producer: Ошибка подключения - {e}")
            raise
    
    def send_message(self, destination: str, message: Dict[str, Any], persistent: bool = True):
        
        try:
            
            message['timestamp'] = datetime.now().isoformat()
            message['source'] = 'customer-service'
            
            
            body = json.dumps(message, ensure_ascii=False, default=str)
            
            
            self.conn.send(
                destination=destination,
                body=body,
                persistent='true' if persistent else 'false',
                headers={
                    'content-type': 'application/json',
                    'JMS_DeliveryMode': 2 if persistent else 1  # 2 = PERSISTENT
                }
            )
            logger.info(f"JMS: Сообщение отправлено в {destination}")
            return True
        except Exception as e:
            logger.error(f"JMS: Ошибка отправки - {e}")
            return False
    
    def send_customer_event(self, event_type: str, customer_data: Dict[str, Any]):
       
        queue_map = {
            'CREATED': QUEUE_NAMES['CUSTOMER_CREATED'],
            'UPDATED': QUEUE_NAMES['CUSTOMER_UPDATED'],
            'DELETED': QUEUE_NAMES['CUSTOMER_DELETED']
        }
        
        if event_type in queue_map:
            queue = queue_map[event_type]
            
            destination = f"/queue/{queue}"
            
            message = {
                'eventType': event_type,
                'customer': customer_data,
                'eventId': f"{event_type}_{customer_data.get('id', 'unknown')}_{datetime.now().timestamp()}"
            }
            
            
            topic_destination = JMS_CONFIG['topics']['customer_events']
            self.send_message(topic_destination, message)
            
            return self.send_message(destination, message)
        return False
    
    def disconnect(self):
        """Закрыть соединение"""
        if self.conn:
            self.conn.disconnect()
            logger.info("JMS Producer: Соединение закрыто")



_jms_producer = None

def get_jms_producer() -> JMSProducer:
    global _jms_producer
    if _jms_producer is None:
        _jms_producer = JMSProducer()
    return _jms_producer