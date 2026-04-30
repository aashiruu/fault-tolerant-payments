## System Flow
1. API receives request + X-Request-ID.
2. Redis checks for duplicate.
3. API writes INITIATED to Postgres.
4. API pushes job to RabbitMQ.
5. Worker processes job -> updates Postgres to SUCCESS/FAILED.

## Failure Handling
- **Redis Down:** API Fails-Closed (503 Error) to prevent double charges.
- **RabbitMQ Down:** API returns 'ACCEPTED_OFFLINE'; system recovers via Reconciliation.
