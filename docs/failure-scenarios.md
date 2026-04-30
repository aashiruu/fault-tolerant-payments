# Failure Scenarios & Test Results

## 1. Duplicate Request Submission
- **Scenario:** Client sends two identical payments with the same X-Request-ID.
- **Mechanism:** Redis SETNX (Atomic Lock).
- **Result:** First request processed; second request returned "Duplicate request detected."
- **Recovery:** No duplicate entry in Postgres; no double-charge in Mock Provider.

## 2. Message Broker (RabbitMQ) Outage
- **Scenario:** API tries to publish a job while RabbitMQ is stopped.
- **Mechanism:** Try/Except block with a 2-second connection timeout.
- **Result:** API returned "ACCEPTED_OFFLINE" instead of hanging/crashing.
- **Recovery:** Payment is safe in Postgres as 'INITIATED'. Reconciliation worker re-queues it once RabbitMQ is up.

## 3. Worker Crash (Mid-Process)
- **Scenario:** Worker killed (Ctrl+C) during a 10s "Chaos Sleep" before acknowledging the message.
- **Mechanism:** RabbitMQ Acknowledgement (Ack) system.
- **Result:** Message returned to 'Unacked' state in queue. Upon worker restart, job was re-consumed.
- **Recovery:** Mock Provider's idempotency ensured the second call didn't create a double-charge.
