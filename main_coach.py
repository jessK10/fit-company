#!/usr/bin/env python
import threading
from src.coach.app import run_app
from src.coach.queue_consumer import run_consumer

def start_consumer():
    """Start the queue consumer in a separate thread"""
    consumer_thread = threading.Thread(target=run_consumer, daemon=True)
    consumer_thread.start()


if __name__ == "__main__":
    # Start the queue consumer in a separate thread
    start_consumer()
    
    # Start the Flask app in the main thread
    run_app()