from fastapi import FastAPI, Header, HTTPException, Depends
from redis import Redis
from sqlalchemy.orm import Session
import os
import uuid

from services.shared.database import SessionLocal
from services.shared.models import Payment, PaymentStatus
from services.shared.messaging import publish_payment_job
from pydantic import BaseModel

app = FastAPI()
redis_client = Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379, db=0, decode_responses=True)

class PaymentRequest(BaseModel):
    amount: float
    currency: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/v1/payments")
async def create_payment(
    request: PaymentRequest,
    x_request_id: str = Header(None),
    db: Session = Depends(get_db)
):
    if not x_request_id:
        raise HTTPException(status_code=400, detail="X-Request-ID header required")

    # Idempotency Check
    is_new = redis_client.set(f"req:{x_request_id}", "LOCKED", nx=True, ex=300)
    if not is_new:
        return {"status": "error", "message": "Duplicate request detected"}

    try:
        # Persist to Postgres
        new_payment = Payment(
            request_id=x_request_id,
            amount=request.amount,
            status=PaymentStatus.INITIATED
        )
        db.add(new_payment)
        db.commit()
        db.refresh(new_payment)

        # Asynchronous handoff
        job_data = {"payment_id": new_payment.id, "request_id": x_request_id}

        try:
            publish_payment_job(job_data)
            return {"payment_id": new_payment.id, "status": "QUEUED"}
        except Exception as e:
            import traceback
            print("!!! RABBITMQ ERROR !!!")
            return {"payment_id": new_payment.id, "status": "ACCEPTED_OFFLINE"}

    except Exception as e:
        import traceback
        print("!!! DATABASE ERROR !!!")
        print(traceback.format_exc())
        db.rollback()
        redis_client.delete(f"req:{x_request_id}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
