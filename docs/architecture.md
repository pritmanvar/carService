# System Architecture Blueprint

This document outlines the high-level system architecture for the AI Automotive Platform, integrating frontend portals, the API gateway, microservices (including AI and Real-time Engines), and the data layers.

## High-Level Architecture Diagram

```mermaid
graph TD
    %% Frontend Clients
    subgraph Frontend Layer
        UP[User Portal\nReact JS, LangGraph UI]
        DP[Dealer Portal\nReact JS]
        Admin[Admin Dashboard\nReact JS]
    end

    %% External Services
    subgraph External & Third-Party Integrations
        OAUTH[OAuth Providers\nGoogle/Apple]
        LLM[OpenAI GPT-4o]
        MDATA[Market Data API\nEdmunds/BlackBook]
        CRM[Dealer CRM\nSalesforce/VinSolutions]
        COMM[SendGrid/Twilio/FCM]
    end

    %% Load Balancer / API Gateway
    AG[API Gateway / Load Balancer\nNGINX / AWS API Gateway]

    %% Backend Microservices
    subgraph Backend Microservices Layer
        CS[Core API Service\nFastAPI, SQLAlchemy]
        AIS[AI Chatbot Service\nLangGraph, FastAPI]
        AE[Auction Engine Service\nFastAPI WebSockets]
        NS[Notification Service\nWorker Process]
        PS[Pricing Engine]
    end

    %% Data Layer
    subgraph Data Layer
        DB[(PostgreSQL\nPrimary DB)]
        CACHE[(Redis\nCache, Pub/Sub, Sessions)]
        STORAGE[(AWS S3\nObject Storage)]
    end

    %% Connections
    UP -->|HTTPS / WSS| AG
    DP -->|HTTPS| AG
    Admin -->|HTTPS| AG

    AG -->|REST/GraphQL| CS
    AG -->|REST| AIS
    AG -->|WSS / WebSockets| AE
    
    CS -->|Read/Write| DB
    CS -->|Cache/Read| CACHE
    CS -->|Uploads| STORAGE
    CS -->|API| CRM
    
    AIS -->|Prompt/Completion| LLM
    AIS -->|Context Query| CS
    AIS -->|Read/Write| DB
    
    AE -->|Pub/Sub| CACHE
    AE -->|Persist Bids| DB
    
    NS -->|Listen Events| CACHE
    NS -->|Send| COMM
    
    PS -->|Query| MDATA
    PS -->|Read/Write| DB

    %% Authentication
    UP -.->|Token| OAUTH
    DP -.->|Token| OAUTH
```

## Component Definitions

### 1. Frontend Layer
- **User Portal**: The B2C interface built in React JS where sellers list cars via the AI chatbot (LangGraph UI) and buyers discover cars and manage reverse bidding. Connects to backend via REST and WebSockets.
- **Dealer Portal**: The B2B interface built in React JS for inventory management, CRM integrations, and active bidding dashboards.

### 2. API Gateway
- Routes incoming HTTP requests to the appropriate microservice (Core API vs AI Service).
- Manages WebSocket connection upgrades routing them directly to the Auction Engine.
- Handles rate-limiting, SSL termination, and initial JWT token validation.

### 3. Backend Microservices
- **Core API Service**: Built on FastAPI and SQLAlchemy. Handles CRUD for users, properties, inventory, roles, etc.
- **AI Chatbot Service**: Built on FastAPI, deploying LangGraph orchestrations and serving the LangGraph UI in React JS. Interacts with OpenAI to execute slot-filling.
- **Auction Engine**: Built on FastAPI WebSockets. Maintains persistent WebSocket connections with active users/dealers. Bids are broadcasted to all subscribed clients via Redis Pub/Sub in under 500ms.
- **Notification Service**: Listens for system events (e.g., `bid_placed`, `auction_won`) from Redis and disperses alerts through SendGrid, Twilio, and FCM.
- **Pricing Engine**: Built on FastAPI. Integrates with external market APIs to estimate car values.

### 4. Data Layer
- **PostgreSQL**: Stores relational, highly-structured data (Users, Vehicles, Bids Audit Trail, Transactions).
- **Redis**: Serves as the high-speed state manager for live auctions and the Pub/Sub broker to scale WebSockets across multiple Auction Engine nodes.
- **S3 / Cloud Storage**: Stores un-structured blobs like car photos and inspection pdfs.
