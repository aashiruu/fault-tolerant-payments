from fastapi import FastAPI, Body
import random
import time

app = FastAPI()

@app.post("/charge")
async def charge(payload: dict = Body(...)):
    # Simulate processing time
    time.sleep(random.uniform(0.1, 0.5))
    
    # Simulate a 10% failure rate for testing fault tolerance
    if random.random() < 0.1:
        return {"status": "failed", "error": "Provider connection timeout"}, 503
        
    return {
        "status": "success",
        "transaction_id": f"txn_{random.randint(10000, 99999)}",
        "message": "Payment processed by mock provider"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
