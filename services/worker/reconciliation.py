import time
from datetime import datetime, timedelta
from services.shared.database import SessionLocal
from services.shared.models import Payment, PaymentStatus
from services.shared.messaging import publish_payment_job

def reconcile():
    db = SessionLocal()
    try:
        # Find payments stuck in INITIATED or PENDING for more than 2 minutes
        threshold = datetime.utcnow() - timedelta(minutes=2)
        stuck_payments = db.query(Payment).filter(
            Payment.status.in_([PaymentStatus.INITIATED, PaymentStatus.PENDING]),
            Payment.updated_at < threshold
        ).all()

        for p in stuck_payments:
            print(f"[!] Reconciling stuck payment: {p.request_id}")
            job_data = {"payment_id": p.id, "request_id": p.request_id}

            # Re-publish to the queue
            publish_payment_job(job_data)

        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    while True:
        print("[*] Running reconciliation sweep...")
        reconcile()
        time.sleep(30)
