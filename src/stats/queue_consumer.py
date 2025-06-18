import json
import pika
import os
from datetime import datetime
from models.workout_stat import WorkoutStat
from db.database import SessionLocal


def callback(ch, method, properties, body):
    print("Received event in stats service")
    data = json.loads(body)

    session = SessionLocal()
    try:
        workout = WorkoutStat(
            user_id=data["user_id"],
            workout_type=data["workout_type"],
            duration_minutes=data["duration_minutes"],
            calories_burned=data["calories_burned"],
            performed_at=datetime.fromisoformat(data["performed_at"])
        )
        session.add(workout)
        session.commit()
        print(f"Saved workout stat for user {data['user_id']}")
    except Exception as e:
        session.rollback()
        print(f"Error saving workout stat: {e}")
    finally:
        session.close()


def start_consumer():
    rabbitmq_host = os.getenv("RABBITMQ_HOST", "localhost")
    rabbitmq_user = os.getenv("RABBITMQ_DEFAULT_USER", "guest")
    rabbitmq_pass = os.getenv("RABBITMQ_DEFAULT_PASS", "guest")

    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)
    parameters = pika.ConnectionParameters(host=rabbitmq_host, credentials=credentials)

    try:
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        channel.exchange_declare(exchange="workout.performed", exchange_type="fanout")
        result = channel.queue_declare(queue="", exclusive=True)
        queue_name = result.method.queue

        channel.queue_bind(exchange="workout.performed", queue=queue_name)
        print("📡 Stats service listening to 'workout.performed' events...")

        channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
        channel.start_consuming()
    except Exception as e:
        print(f" Failed to connect to RabbitMQ: {e}")
