## Handling Broker Outages
**Decision:** Option B (Keep record as INITIATED and return ACCEPTED_OFFLINE).
**Reasoning:** If Postgres is updated but RabbitMQ is down, we should NOT delete the transaction. By keeping it, we ensure we don't lose the customer's intent. A background "Reconciliation Worker" will periodically check for 'INITIATED' payments and re-queue them once RabbitMQ is back up.

## Idempotency Layer
**Tool:** Redis (SETNX).
**Reasoning:** Atomic operations prevent race conditions where two identical requests could process simultaneously.
