from fastapi import FastAPI, Body
import random
import time

app = FastAPI()
processed_requests = {}

@app.post("/charge")
async def charge(data: dict = Body(...)):
    request_id = data.get("request_id")

    # Check if this ID is seen before
    if request_id in processed_requests:
        return {"status": "SUCCESS", "message": "Already processed", "provider_ref": processed_requests[request_id]}

    # Simulate network latency
    time.sleep(1)

    # Simulate random provider failure (10% of the time)
    if random.random() < 0.1:
        return {"status": "FAILED", "message": "Provider timeout"}

    # Success path
    ref = f"ref_{random.randint(1000, 9999)}"
    processed_requests[request_id] = ref
    return {"status": "SUCCESS", "provider_ref": ref}
