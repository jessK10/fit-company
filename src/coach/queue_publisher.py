import json
import pika
import os

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_USER = os.getenv("RABBITMQ_DEFAULT_USER", "rabbit")
RABBITMQ_PASS = os.getenv("RABBITMQ_DEFAULT_PASS", "docker")

credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
params = pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials)

connection = pika.BlockingConnection(params)
channel = connection.channel()

# Step 2: Declare the exchange (fanout)
channel.exchange_declare(exchange='workout.performed', exchange_type='fanout')

def publish_workout_event(event_data: dict):
    """Publish a workout event to the workout.performed exchange"""
    message = json.dumps(event_data)
    channel.basic_publish(exchange='workout.performed', routing_key='', body=message)
    print(" Published workout event:", message)
