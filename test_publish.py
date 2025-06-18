import pika, json
import datetime

credentials = pika.PlainCredentials("rabbit", "docker")
parameters = pika.ConnectionParameters(
    host="localhost",  # because RabbitMQ port 5672 is mapped to 12104
    port=12104,
    credentials=credentials
)

connection = pika.BlockingConnection(parameters)
channel = connection.channel()

channel.exchange_declare(exchange="workout.performed", exchange_type="fanout")

message = {
    "user_id": 1,
    "workout_type": "Cardio",
    "duration_minutes": 45,
    "calories_burned": 300,
    "performed_at": datetime.datetime.utcnow().isoformat()
}

channel.basic_publish(
    exchange="workout.performed",
    routing_key="",
    body=json.dumps(message)
)

print("✅ Sent message to workout.performed queue")
