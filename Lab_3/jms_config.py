# jms_config.py
# Конфигурация подключения к ActiveMQ Artemis

JMS_CONFIG = {
    'host': 'localhost',
    'port': 61613,
    'login': 'admin',
    'passcode': 'admin',
    'queues': {
        'email': '/queue/email.queue',
        'audit': '/queue/audit.queue',
        'notification': '/queue/notification.queue'
    },
    'topics': {
        'customer_events': '/topic/customer.events.topic'
    }
}

QUEUE_NAMES = {
    'CUSTOMER_CREATED': 'customer.created.queue',
    'CUSTOMER_UPDATED': 'customer.updated.queue',
    'CUSTOMER_DELETED': 'customer.deleted.queue',
}