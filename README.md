# Fault-Tolerant Payment Engine

A production-grade, asynchronous payment processing system engineered for high reliability, idempotency, and full observability. Deployed on **AWS EKS** via **Terraform** and **GitHub Actions**.

## 🏗 System Architecture
The system utilizes a decoupled, event-driven architecture to ensure that payment ingestion is non-blocking and processing is resilient to downstream failures.

```mermaid
graph TD
    User((User/Client)) -->|1. POST /v1/payments| API[Payment API - FastAPI]
    
    subgraph "Ingestion & Safety"
        API -->|2. Check/Set ID| Redis[(Redis - Idempotency)]
        API -->|3. Create Record| DB[(Postgres - Payments DB)]
        API -->|4. Publish Job| RMQ[RabbitMQ - Jobs Queue]
    end

    subgraph "Asynchronous Processing"
        RMQ -->|5. Consume| Worker[Payment Worker - Python]
        Worker -->|6. POST /charge| Provider[Mock Provider - Flask]
        Worker -->|7. Update Status| DB
    end

    subgraph "SRE Observability"
        Prom[Prometheus] -->|Scrape /metrics| API
        Prom -->|Scrape /metrics| Worker
        Prom -->|Data Source| Grafana[Grafana Dashboards]
    end
```

## 🚀 Key Engineering Features
* **Distributed Idempotency:** Implemented a Redis-based locking mechanism using `X-Request-ID` headers to prevent duplicate transactions (double-charging) in high-concurrency scenarios.
* **Event-Driven Resiliency:** Leverages RabbitMQ as a durable message broker. If the worker or the external payment provider is unavailable, payment jobs are persisted in the queue and processed automatically upon recovery.
* **Database Schema Design:** Relational Postgres schema designed for transactional integrity, tracking the full lifecycle of a payment from `QUEUED` to `PENDING` to `SUCCESS`.
* **Infrastructure as Code (IaC):** 100% automated provisioning of VPC, Subnets, NAT Gateways, and EKS Cluster using modular Terraform.

## 🛠 Technical Challenges & War Stories
### 1. The DNS Discovery Problem
**Challenge:** Initially, the Worker service could not resolve the Provider's internal K8s service name, causing processing loops.
**Solution:** Diagnosed the CoreDNS resolution path within the EKS VPC and updated the worker's environment configuration to use the fully qualified domain name (FQDN) `payment-provider.default.svc.cluster.local`.

### 2. Status Normalization Logic
**Challenge:** Payments were failing to transition to a 'SUCCESS' state because the external mock provider returned uppercase status strings while the worker expected lowercase.
**Solution:** Implemented string normalization in the processing logic to ensure the state machine is robust against varying third-party API response formats.

### 3. Multi-Account Migration
**Challenge:** Successfully migrated the entire infrastructure stack between two separate AWS accounts in under 15 minutes.
**Solution:** Leveraged Terraform's state management and account-agnostic CI/CD pipelines to recreate the environment with zero code changes, demonstrating true environment portability.

## 📊 Observability Proof-of-Work

### CI/CD Pipeline
Fully automated Build-Test-Deploy pipeline in GitHub Actions.
![Pipeline](docs/pipeline-success.png)

### SRE Dashboards
Real-time monitoring of CPU/Memory saturation and network throughput.
![Resources](docs/resource-usage.png)
![Network](docs/network-metrics.png)

### Cluster Orchestration
High-availability pod distribution across EKS nodes.
![Pods](docs/pods-running.png)

## 🛠 Deployment & Local Setup
### To Deploy to AWS:
1.  Initialize infrastructure: `cd infra/terraform && terraform apply`
2.  Update GitHub Secrets with new AWS credentials.
3.  Push to `master` to trigger the automated rollout.

---
*Developed by Okikiola Ashiru — Cloud & DevOps Engineer*
