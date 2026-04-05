

import stomp
import json
import logging
import threading
import time
from typing import Dict, Any, Callable, Optional
from datetime import datetime
from jms_config import JMS_CONFIG, QUEUE_NAMES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JmsListenerContainerFactory:
    
    
    def __init__(self):
        self.pub_sub_domain = False  # False для очередей, True для топиков
        self.concurrency_min = 1
        self.concurrency_max = 5
        self.session_transacted = True
        self.auto_startup = True
    
    def set_pub_sub_domain(self, is_topic: bool):
        
        self.pub_sub_domain = is_topic
    
    def set_concurrency(self, concurrency: str):
        
        if '-' in concurrency:
            parts = concurrency.split('-')
            self.concurrency_min = int(parts[0])
            self.concurrency_max = int(parts[1])
        else:
            self.concurrency_min = self.concurrency_max = int(concurrency)
    
    def set_session_transacted(self, transacted: bool):
        
        self.session_transacted = transacted
    
    def create_listener_container(self, destination: str, handler: Callable) -> 'JmsListenerContainer':
        
        container = JmsListenerContainer(
            destination=destination,
            handler=handler,
            pub_sub_domain=self.pub_sub_domain,
            concurrency_min=self.concurrency_min,
            concurrency_max=self.concurrency_max,
            session_transacted=self.session_transacted
        )
        return container


class JmsListenerContainer:
   
    
    def __init__(self, destination: str, handler: Callable, 
                 pub_sub_domain: bool = False,
                 concurrency_min: int = 1, 
                 concurrency_max: int = 5,
                 session_transacted: bool = True):
        self.destination = destination
        self.handler = handler
        self.pub_sub_domain = pub_sub_domain
        self.concurrency_min = concurrency_min
        self.concurrency_max = concurrency_max
        self.session_transacted = session_transacted
        self.running = False
        self.threads = []
        self.connections = []
    
    def start(self):
        
        if self.running:
            logger.warning(f"Container for {self.destination} already running")
            return
        
        self.running = True
        num_threads = self.concurrency_min
        
        logger.info(f" Запуск JMS Listener Container для {self.destination}")
        logger.info(f"   Режим: {'ТОПИК' if self.pub_sub_domain else 'ОЧЕРЕДЬ'}")
        logger.info(f"   Потоков: {num_threads} (min={self.concurrency_min}, max={self.concurrency_max})")
        logger.info(f"   Транзакционность: {'ВКЛ' if self.session_transacted else 'ВЫКЛ'}")
        
        for i in range(num_threads):
            thread = threading.Thread(
                target=self._run_listener,
                args=(i,),
                daemon=True
            )
            thread.start()
            self.threads.append(thread)
    
    def _run_listener(self, thread_id: int):
        
        retry_count = 0
        max_retries = 5
        
        while self.running and retry_count < max_retries:
            conn = None
            try:
                
                conn = stomp.Connection(
                    host_and_ports=[(JMS_CONFIG['host'], JMS_CONFIG['port'])],
                    auto_content_length=False,
                    heartbeats=(10000, 10000)
                )
                self.connections.append(conn)
                
                
                listener = StompMessageListener(self.handler, thread_id, self.session_transacted)
                conn.set_listener('', listener)
                
                
                conn.connect(
                    login=JMS_CONFIG['login'],
                    passcode=JMS_CONFIG['passcode'],
                    wait=True
                )
                
                logger.info(f" [Поток {thread_id}] Подключен к {self.destination}")
                
                
                subscription_id = f"sub-{self.destination}-{thread_id}"
                conn.subscribe(
                    destination=self.destination, 
                    id=subscription_id, 
                    ack='client-individual' if self.session_transacted else 'auto'
                )
                
                logger.info(f" [Поток {thread_id}] Подписан на {self.destination}")
                
                retry_count = 0
                
                
                while self.running:
                    time.sleep(1)
                    
            except Exception as e:
                retry_count += 1
                logger.error(f" [Поток {thread_id}] Ошибка: {e}")
                if retry_count < max_retries:
                    time.sleep(5)
                    
            finally:
                if conn:
                    try:
                        conn.disconnect()
                    except:
                        pass
        
        logger.info(f" [Поток {thread_id}] Остановлен для {self.destination}")
    
    def stop(self):
        """Остановка контейнера"""
        self.running = False
        for thread in self.threads:
            thread.join(timeout=5)
        for conn in self.connections:
            try:
                conn.disconnect()
            except:
                pass
        logger.info(f" JMS Listener Container для {self.destination} остановлен")


class StompMessageListener(stomp.ConnectionListener):
    
    
    def __init__(self, handler: Callable, thread_id: int, session_transacted: bool = True):
        self.handler = handler
        self.thread_id = thread_id
        self.session_transacted = session_transacted
        super().__init__()
    
    def on_message(self, frame):
        """Обработка полученного сообщения"""
        try:
            destination = frame.headers.get('destination', 'unknown')
            body = json.loads(frame.body)
            
            logger.info(f" [Поток {self.thread_id}] Получено сообщение из {destination}")
            
            
            self.handler(body)
            
            
            if self.session_transacted and frame.headers.get('ack'):
                
                pass
                
        except Exception as e:
            logger.error(f" [Поток {self.thread_id}] Ошибка обработки: {e}")
            if self.session_transacted:
                # В транзакционном режиме можно отправить отрицательное подтверждение
                pass
            raise e


class JMSConsumer:
   
    
    def __init__(self):
        self.containers = []
        self.queue_factory = None
        self.topic_factory = None
        self._initialized = False
    
    def _init_factories(self):
        
        if self._initialized:
            return
        
        # Фабрика для очередей (queueListenerFactory)
        self.queue_factory = JmsListenerContainerFactory()
        self.queue_factory.set_pub_sub_domain(False)  # false для очередей
        self.queue_factory.set_concurrency("1-5")     # от 1 до 5 потоков
        self.queue_factory.set_session_transacted(True)  
        
        
        self.topic_factory = JmsListenerContainerFactory()
        self.topic_factory.set_pub_sub_domain(True)   
        self.topic_factory.set_concurrency("1-3")
        self.topic_factory.set_session_transacted(True)
        
        self._initialized = True
    
    def start(self, handlers: Dict[str, Callable]):
        
        self._init_factories()
        
        for destination, handler in handlers.items():
            
            if '/topic/' in destination:
                factory = self.topic_factory
            else:
                factory = self.queue_factory
            
            
            container = factory.create_listener_container(destination, handler)
            container.start()
            self.containers.append(container)
            
            logger.info(f" Зарегистрирован JMS слушатель для {destination}")
    
    def stop(self):
        """Остановка всех контейнеров"""
        for container in self.containers:
            container.stop()
        self.containers.clear()
        logger.info(" Все JMS слушатели остановлены")


# Глобальный экземпляр
_jms_consumer = None

def get_jms_consumer() -> JMSConsumer:
    global _jms_consumer
    if _jms_consumer is None:
        _jms_consumer = JMSConsumer()
    return _jms_consumer