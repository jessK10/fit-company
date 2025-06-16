import os
import pika
import json
import logging
from typing import Dict, Any

from .queue_messages import CreateWodMessage

from .fitness_coach_service import create_wod_for_user

logger = logging.getLogger(__name__)

# Disable pika logging 
logging.getLogger("pika").setLevel(logging.WARNING)

class WodQueueConsumer:
    _instance = None
    _is_initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WodQueueConsumer, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._is_initialized:
            self.connection = None
            self.channel = None
            self.queue_name = "createWodQueue"
            self._is_initialized = True
            self.connect()
            logger.info("WodQueueConsumer initialized and connected to RabbitMQ")

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
            arguments={
                "x-message-ttl": 60000,  # 1 minutes
                "x-max-length": 100,
                "x-dead-letter-exchange": "dlx",
                "x-dead-letter-routing-key": f"{self.queue_name}-dead"
            }
        )
        logger.info(f"Successfully connected to RabbitMQ and declared queue '{self.queue_name}'")

    def onCreateWodMessage(self, ch, method, properties, body):
        """Handle received messages"""
        try:
            logger.info(f"Starting to process message with delivery-tag: {method.delivery_tag}")
            
            message = CreateWodMessage.model_validate_json(body)
            logger.debug(f"Successfully parsed message: {message.model_dump_json()}")
            
            # Extract user email from message
            user_email = message.email
            
            try:
                exercises_with_muscles = create_wod_for_user(user_email)
                if not exercises_with_muscles or not exercises_with_muscles[0]:
                    raise ValueError("No exercises generated for WOD")
                    
                logger.info(f"Successfully generated WOD for user {user_email} with {len(exercises_with_muscles)} exercise groups")
                
                # Acknowledge message only after successful processing
                ch.basic_ack(delivery_tag=method.delivery_tag)
                logger.debug(f"Successfully acknowledged message {method.delivery_tag}")
                
            except Exception as service_error:
                logger.error(f"Error in request_wod service for user {user_email}: {str(service_error)}", exc_info=True)
                # Negative acknowledge and don't requeue if it's a service error
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                return
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode message: {str(e)}")
            # Don't requeue if the message is malformed
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        except Exception as e:
            logger.error(f"Unexpected error processing message: {str(e)}", exc_info=True)
            # Requeue only for unexpected errors
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def start_consuming(self):
        """Start consuming messages from the queue"""
        try:
            self.ensure_connection()
            
            # Set up consumer with QoS
            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=self.onCreateWodMessage
            )
            
            logger.info(f"Started consuming from queue '{self.queue_name}'")
            self.channel.start_consuming()
            
        except KeyboardInterrupt:
            logger.info("Received shutdown signal, stopping consumer...")
            self.stop()
        except Exception as e:
            logger.error(f"Error in consumer: {str(e)}", exc_info=True)
            self.stop()

    def stop(self):
        """Stop the consumer and close connection"""
        try:
            if self.channel and self.channel.is_open:
                self.channel.stop_consuming()
                logger.info("Stopped consuming messages")
            
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                logger.info("Closed RabbitMQ connection")
        except Exception as e:
            logger.error(f"Error while stopping consumer: {str(e)}", exc_info=True)


def run_consumer():
    # Create a singleton instance
    wod_queue_consumer = WodQueueConsumer()
    """Entry point to start the consumer"""
    # try:
    logger.info("Starting consumer")
    wod_queue_consumer.start_consuming()
