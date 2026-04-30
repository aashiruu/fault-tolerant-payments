import pika
import json
import os

def publish_payment_job(payment_data):
    params = pika.ConnectionParameters(
        host=os.getenv("RABBITMQ_HOST", "localhost"),
        connection_attempts=1,
        retry_delay=1,
        socket_timeout=2
    )

    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue='payment_jobs', durable=True)

    channel.basic_publish(
        exchange='',
        routing_key='payment_jobs',
        body=json.dumps(payment_data),
        properties=pika.BasicProperties(delivery_mode=2)
    )
    connection.close()
