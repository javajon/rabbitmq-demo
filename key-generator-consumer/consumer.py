#!/usr/bin/env python3
import pika
import json
import uuid
import time
from datetime import datetime
import os
import sys

# RabbitMQ Configuration
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq.rabbitmq.svc.cluster.local')
RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', '5672'))
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'guest')
REQUEST_QUEUE = os.getenv('REQUEST_QUEUE', 'key-requests')
RESPONSE_QUEUE = os.getenv('RESPONSE_QUEUE', 'generated-keys')

def generate_key():
    """Generate a UUID key with a small delay to simulate processing"""
    time.sleep(1)  # Simulate processing time
    return str(uuid.uuid4())

def process_request(ch, method, properties, body):
    """Process key generation request"""
    try:
        # Parse the incoming request
        request_data = json.loads(body)
        request_id = request_data.get('requestId')

        print(f"[{datetime.now()}] Received key request: {request_id}")

        # Generate the key
        generated_key = generate_key()

        # Create response message
        response = {
            'requestId': request_id,
            'key': generated_key,
            'generatedAt': datetime.now().isoformat()
        }

        # Send response back to the response queue
        ch.basic_publish(
            exchange='',
            routing_key=RESPONSE_QUEUE,
            body=json.dumps(response),
            properties=pika.BasicProperties(
                content_type='application/json',
                delivery_mode=2  # Make message persistent
            )
        )

        print(f"[{datetime.now()}] Generated key {generated_key} for request {request_id}")

        # Acknowledge the message
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"Error processing request: {e}", file=sys.stderr)
        # Reject and requeue the message on error
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def main():
    """Main consumer loop"""
    print(f"[{datetime.now()}] Starting Key Generator Consumer")
    print(f"  RabbitMQ Host: {RABBITMQ_HOST}:{RABBITMQ_PORT}")
    print(f"  Request Queue: {REQUEST_QUEUE}")
    print(f"  Response Queue: {RESPONSE_QUEUE}")

    # Retry connection logic
    max_retries = 10
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            # Connect to RabbitMQ
            credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
            parameters = pika.ConnectionParameters(
                host=RABBITMQ_HOST,
                port=RABBITMQ_PORT,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )

            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()

            # Declare queues (idempotent operation)
            channel.queue_declare(queue=REQUEST_QUEUE, durable=True)
            channel.queue_declare(queue=RESPONSE_QUEUE, durable=True)

            # Set prefetch count to process one message at a time
            channel.basic_qos(prefetch_count=1)

            # Start consuming
            channel.basic_consume(
                queue=REQUEST_QUEUE,
                on_message_callback=process_request
            )

            print(f"[{datetime.now()}] Waiting for key generation requests. To exit press CTRL+C")
            channel.start_consuming()

        except pika.exceptions.AMQPConnectionError as e:
            print(f"Connection attempt {attempt + 1}/{max_retries} failed: {e}", file=sys.stderr)
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...", file=sys.stderr)
                time.sleep(retry_delay)
            else:
                print("Max retries reached. Exiting.", file=sys.stderr)
                sys.exit(1)
        except KeyboardInterrupt:
            print(f"\n[{datetime.now()}] Shutting down consumer...")
            if 'connection' in locals():
                connection.close()
            sys.exit(0)
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            if 'connection' in locals():
                connection.close()
            sys.exit(1)

if __name__ == '__main__':
    main()
