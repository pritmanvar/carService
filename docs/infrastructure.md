# Cloud Infrastructure Blueprint (AWS)

This document dictates the production-ready infrastructure blueprint for the AI Automotive Platform built on Amazon Web Services (AWS), mapping heavily to the Containerised Microservices architecture.

## 1. Network Topology (VPC Design)
- **Virtual Private Cloud (VPC)**: Created across 3 Availability Zones (AZs) for high availability.
- **Public Subnets**: Contains public-facing resources like the Application Load Balancer (ALB) and NAT Gateways.
- **Private Subnets (App Tier)**: Houses the EKS/ECS worker nodes running the microservices. No inbound internet access.
- **Private Subnets (Data Tier)**: Houses RDS PostgreSQL and ElastiCache Redis. Strictly accessible only from the App Tier.

## 2. Compute (EKS / ECS)
- **Container Orchestration**: Elastic Kubernetes Service (EKS) is recommended to manage the different microservices (API, Chatbot, Auction).
- **Node Groups**: EC2 instances forming the worker nodes running within the App Tier Private Subnet.
- **Auto Scaling**: Horizontal Pod Autoscaler (HPA) triggers scaling based on CPU/Memory and WebSocket connection count.

## 3. Data Storage
- **Primary Database**: Amazon RDS for PostgreSQL (Multi-AZ deployment).
- **In-Memory Cache & Pub/Sub**: Amazon ElastiCache for Redis (Cluster Mode Enabled) for low-latency WebSocket bidding and API caching.
- **Object Storage**: Amazon S3. Configured with separate buckets:
  - `ai-auto-platform-public-assets` (Car photos, public thumbnails - attached to CloudFront).
  - `ai-auto-platform-private-docs` (Dealer licenses, sensitive pdfs).

## 4. Edge & Delivery
- **CDN**: Amazon CloudFront to cache and securely deliver Next.js static assets and S3 images globally.
- **Load Balancing**: Application Load Balancer (ALB) acting as the single entry point. Configured with a Web Application Firewall (WAF).
- **DNS**: Route 53 pointing apex domains and subdomains to CloudFront/ALB.

## 5. Third-Party Connections
- System interacts with SendGrid, Twilio, OpenAI, and Dealer CRMs through NAT Gateways located in the public subnets, allowing safe outbound-only connections from the microservices.

## 6. Diagram Flow
```text
[ Users / Dealers ]
       |
     (WAF)
       |
[ ALB / CloudFront ]
       |
------------- Private App Subnet -------------
|   [ EKS / ECS Cluster ]                    |
|     - Next.js UI Pods                      |
|     - Core API Pods                        |
|     - Chatbot (FastAPI) Pods               |
|     - Auction Engine (Node.js/Socket) Pods |
----------------------------------------------
       |
------------- Private Data Subnet ------------
|   [ RDS PostgreSQL ]  [ ElastiCache Redis ]|
----------------------------------------------
```

## Document Data Retention & Archival Policy
1. **Chatbot Logs**: Retained in active PostgreSQL for 90 days. Archived to S3 Glacier for 2 years (compliance/training).
2. **Auction Audit Trail**: Immutable table logic, kept in hot storage for 1 year. Archived to S3 Glacier for 5 years for dispute resolution.
3. **Images**: Deleted from S3 automatically 30 days after a car listing is marked as `SOLD` and transaction completely settled.
4. **PII**: Managed by strict GDPR compliance requests; right-to-erase triggers wiping user identifying rows while anonymizing past auction bids.
