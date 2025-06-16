import os
import pika
import json
import logging
from typing import Dict, Any

from ..queue_messages import CreateWodMessage

logger = logging.getLogger(__name__)

# Disable pika logging 
logging.getLogger("pika").setLevel(logging.WARNING)

class RabbitMQService:
    _instance = None
    _is_initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RabbitMQService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._is_initialized:
            self.connection = None
            self.channel = None
            self.queue_name = "createWodQueue"
            self._is_initialized = True

    def ensure_connection(self):
        """Ensure connection is established"""
        if not self.connection or self.connection.is_closed:
            self.connect()

    def connect(self):
        """Establish connection to RabbitMQ server"""
        logger.debug("Attempting to connect to RabbitMQ")
        credentials = pika.PlainCredentials(
            username=os.getenv("RABBITMQ_DEFAULT_USER", "rabbit"),
            password=os.getenv("RABBITMQ_DEFAULT_PASS", "docker")
        )
        parameters = pika.ConnectionParameters(
            host=os.getenv("RABBITMQ_HOST", "rabbitmq"),
            port=5672,
            credentials=credentials,
            heartbeat=600,
            blocked_connection_timeout=300
        )
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()

        # Declare the main queue with message TTL of 10 minutes (600000 ms)
        # and max length of 100 messages
        arguments = {
            "x-message-ttl": 60000,  # 1 minute
            "x-max-length": 100,
            "x-dead-letter-exchange": "dlx",  # Dead Letter Exchange
            "x-dead-letter-routing-key": f"{self.queue_name}-dead"
        }
        
        # Declare the Dead Letter Exchange and Queue
        self.channel.exchange_declare(exchange="dlx", exchange_type="direct")
        self.channel.queue_declare(queue=f"{self.queue_name}-dead", durable=True)
        self.channel.queue_bind(
            exchange="dlx",
            queue=f"{self.queue_name}-dead",
            routing_key=f"{self.queue_name}-dead"
        )

        # Declare the main queue
        self.channel.queue_declare(
            queue=self.queue_name,
            durable=True,
            arguments=arguments
        )
        logger.info(f"Successfully connected to RabbitMQ and declared queue '{self.queue_name}'")

    def publish_message(self, message: CreateWodMessage) -> bool:
        """Publish a message to the queue"""
        try:
            self.ensure_connection()
            
            message_data = message.model_dump()
            logger.debug(f"Publishing message to queue '{self.queue_name}': {message_data}")
            
            self.channel.basic_publish(
                exchange="",
                routing_key=self.queue_name,
                body=json.dumps(message_data),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                )
            )
            logger.info(f"Successfully published create WOD message for user: {message_data.get('email', 'unknown')}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish message to RabbitMQ: {str(e)}", exc_info=True)
            return False

    def close(self):
        """Close the connection"""
        if self.connection and not self.connection.is_closed:
            logger.info("Closing RabbitMQ connection")
            self.connection.close()

# Create a singleton instance
rabbitmq_service = RabbitMQService() 