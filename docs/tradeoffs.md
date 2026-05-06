## Handling Broker Outages
**Decision:** Option B (Keep record as INITIATED and return ACCEPTED_OFFLINE).
**Reasoning:** If Postgres is updated but RabbitMQ is down, we should NOT delete the transaction. By keeping it, we ensure we don't lose the customer's intent. A background "Reconciliation Worker" will periodically check for 'INITIATED' payments and re-queue them once RabbitMQ is back up.

## Idempotency Layer
**Tool:** Redis (SETNX).
**Reasoning:** Atomic operations prevent race conditions where two identical requests could process simultaneously.

## Security vs. Internal Leaks
**Decision:** Transition from Integer IDs to UUIDs for public responses.
**Reasoning:** Prevents enumeration attacks where an actor could guess total transaction volume or scrape data by incrementing IDs.

## Network Topology: Public vs. Private Subnets
**Decision:** Postgres and Workers live in Private Subnets. API Load Balancer in Public Subnet.
**Reasoning:** This minimizes the attack surface. The Database and Workers do not need to be reachable from the internet; they only need to talk to each other and the internal API. Only the Load Balancer is exposed to handle client traffic.

## Network Topology: Public vs. Private Subnets
**Decision:** We place the Postgres Database and Payment Workers in Private Subnets, while the API Load Balancer resides in Public Subnets.
**Reasoning:** This architecture provides "Defense in Depth" by ensuring the most sensitive components (containing transaction data and processing logic) have no direct route from the public internet, significantly reducing the attack surface. Only the Load Balancer is exposed to handle client traffic, acting as a controlled entry point that forwards requests internally.
