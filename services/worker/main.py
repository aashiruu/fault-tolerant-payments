import pika
import json
import time
import os
import requests
from services.shared.database import SessionLocal
from services.shared.models import Payment, PaymentStatus
from prometheus_client import start_http_server, Counter, Histogram

# Metrics
PAYMENT_COUNT = Counter('payment_processed_total', 'Total payments processed', ['status'])
PAYMENT_LATENCY = Histogram('payment_processing_seconds', 'Time spent processing payment')

# Start Prometheus metrics server on port 8002
start_http_server(8002)

def process_payment(ch, method, properties, body):
    data = json.loads(body)
    payment_id = data.get("payment_id")
    request_id = data.get("request_id")

    db = SessionLocal()
    # Start timing the operation
    with PAYMENT_LATENCY.time():
        try:
            payment = db.query(Payment).filter(Payment.id == payment_id).first()

            # Defensive check: if payment doesn't exist or is already done
            if not payment or payment.status in [PaymentStatus.SUCCESS, PaymentStatus.FAILED]:
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return

            # Update to PENDING
            payment.status = PaymentStatus.PENDING
            db.commit()

            provider_url = os.getenv('PROVIDER_URL', 'http://localhost:8001/charge')

            response = requests.post(
                provider_url,
                json={"request_id": request_id, "amount": 100.0},
                timeout=10
            )
            res_data = response.json()

            # Update final state
            if res_data["status"].upper() == "SUCCESS":
                payment.status = PaymentStatus.SUCCESS
            else:
                payment.status = PaymentStatus.FAILED

            db.commit()

            # Observability: Increment the counter with the specific result
            PAYMENT_COUNT.labels(status=payment.status.value).inc()

            ch.basic_ack(delivery_tag=method.delivery_tag)
            print(f"[*] Payment {payment_id} processed: {payment.status}")

        except Exception as e:
            print(f"[!] Worker Error: {e}")
            db.rollback()
            # Re-queue for retry
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        finally:
            db.close()

def start_worker():
    rabbitmq_host = os.getenv('RABBITMQ_HOST', 'localhost')

    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
    channel = connection.channel()
    channel.queue_declare(queue='payment_jobs', durable=True)

    channel.basic_qos(prefetch_count=1)

    channel.basic_consume(queue='payment_jobs', on_message_callback=process_payment)
    print(f" [*] Worker started (Host: {rabbitmq_host}). Waiting for messages.")
    channel.start_consuming()

if __name__ == "__main__":
    start_worker()
