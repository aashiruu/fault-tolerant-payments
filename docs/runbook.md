# Runbook: Stuck Payments

## Issue: Payment in PENDING for > 5 minutes
This happens if a worker crashes after calling the provider but before updating the database.

## Resolution:
1. Check RabbitMQ Management UI (localhost:15672) for 'Unacked' messages.
2. Restart worker pods/processes.
3. The worker is idempotent; it will safely re-query the provider and update the state to SUCCESS/FAILED.
