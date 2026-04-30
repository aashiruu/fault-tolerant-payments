## System Flow
1. API receives request + X-Request-ID.
2. Redis checks for duplicate.
3. API writes INITIATED to Postgres.
4. API pushes job to RabbitMQ.
5. Worker processes job -> updates Postgres to SUCCESS/FAILED.

## Failure Handling
- **Redis Down:** API Fails-Closed (503 Error) to prevent double charges.
- **RabbitMQ Down:** API returns 'ACCEPTED_OFFLINE'; system recovers via Reconciliation.

## Observability Layer
- **Tool:** Prometheus + Grafana.
- **Metrics:**
    - `payment_processed_total`: Tracks Success/Failure counts.
    - `payment_processing_seconds`: Measures latency of the Mock Provider calls.
- **Goal:** Real-time alerting on high error rates or processing delays.

## The Reconciliation "Janitor"
- **Purpose:** Handles "lost" payments that were saved to DB but never made it to the Queue (or were dropped).
- **Logic:** Periodically scans for payments stuck in 'INITIATED' for > 2 minutes and re-triggers the RabbitMQ publish event.
