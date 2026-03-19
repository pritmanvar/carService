# AI Automotive Platform - Tech Stack Finalisation Document

## 1. Architectural Approach: Microservices vs Monolith
**Recommendation: Modular Microservices Architecture**
Given the distinct scaling requirements of the different components (e.g., the Auction Engine requires high concurrency and low latency via WebSockets, while the AI Chatbot requires heavy compute integration with LLMs), a microservices approach is recommended. 
- **Core API Service**: Handles standard CRUD operations for users, dealers, and vehicle inventory. Built with FastAPI.
- **Auction Engine Service**: Dedicated FastAPI service for managing real-time websocket connections and Redis Pub/Sub for live bidding.
- **AI Chatbot Service**: Dedicated Python/FastAPI service heavily optimized for LangChain/LangGraph orchestration, serving the LangGraph UI in React JS.
- **Notification Service**: Asynchronous worker processing background events for emails, SMS, and push notifications.

## 2. Frontend Layer
- **Framework**: Frontend portals (User & Dealer) will be built using **React JS**. This includes the LangGraph UI integration for the chatbot experience. React JS provides fast client-side routing for authenticated portals.
- **Styling**: **Tailwind CSS** for rapid UI development and maintaining a consistent design system.
- **Real-time Client**: **Socket.io-client** or native WebSockets for receiving live auction bids and reverse-bidding updates.
- **State Management**: Zustand or Redux Toolkit.

## 3. Backend Layer
- **API Gateway / Core Service**: **Python (FastAPI)**. FastAPI provides high performance and native async support for building robust APIs.
- **Real-time Engine**: **FastAPI WebSockets** backend, horizontally scaled using **Redis Pub/Sub** adapter. Target latency is <500ms.
- **AI Integration**: **Python (FastAPI)** with **LangChain/LangGraph** for orchestrating multi-turn dialogues, connecting to the **OpenAI GPT-4o API**. The LangGraph UI will be built natively in React JS.

## 4. Data Layer
- **Primary Relational Database**: **PostgreSQL**. Used for strongly consistent data: users, dealers, car inventory, persistent bid history, and transactions. Data access is managed through **SQLAlchemy (ORM)**.
- **In-Memory Store / Cache**: **Redis**. Used for session management, fast caching of pricing estimates, and acting as the Pub/Sub message broker for the auction engine and live feeds.
- **File Storage**: **AWS S3** (or equivalent Azure Blob / GCP Cloud Storage) for car images, documents, and assets. Served via a CDN (e.g., CloudFront).

## 5. Third-Party Integrations & Services
- **Authentication**: **JWT** for stateless session tokens, integrated with **OAuth 2.0** for Google/Apple social sign-ins.
- **Notifications**: 
  - Email: **SendGrid**
  - SMS: **Twilio**
  - Push: **Firebase Cloud Messaging (FCM)**
- **Market Pricing API**: Integration with Black Book, Edmunds, or equivalent (Client supplied).
- **Dealer CRM Webhooks**: Standardized REST endpoints/webhooks to sync with Salesforce, VinSolutions, DealerSocket.

## 6. Infrastructure & Deployment (Cloud Blueprint Preview)
- **Cloud Provider**: AWS (Recommended) / Azure / GCP.
- **Containerisation**: **Docker** images for all backend services.
- **Orchestration**: **Kubernetes (EKS/AKS/GKE)** or managed container services like AWS ECS / Google Cloud Run.
- **CI/CD**: **GitHub Actions** for automated testing, building Docker images, and deploying to staging/production environments.

## 7. Security & Compliance
- **Data Protection**: PII redaction in AI prompts. AES-256 encryption at rest for sensitive DB fields. TLS 1.3 for data in transit.
- **OWASP**: Penetration testing against OWASP Top 10 prior to launch.
- **Compliance**: GDPR compliance workflows (Right to be Forgotten, Data Export) and Cookie Consent mechanisms.
