# Entity-Relationship (ER) Diagram

This document outlines the core relations and entities required for the AI Automotive Platform. 
The schema must support Standard E-Commerce workflows, structured Multi-turn Chatbot context mappings, and fast query execution for Auction/Pricing Engines.

## Core Entities
1. **Users (Buyers & Sellers)**
2. **Dealers (B2B Accounts)**
3. **Vehicles (Car Listings)**
4. **Auctions (Forward & Reverse)**
5. **Bids (Auction Bids)**
6. **Transactions (Won Auctions)**
7. **ChatSessions (AI Conversation Context)**

## Mermaid ER Diagram

```mermaid
erDiagram
    USERS {
        uuid id PK
        string email
        string password_hash
        string first_name
        string last_name
        string phone
        string role "USER|ADMIN"
        timestamp created_at
    }

    DEALERS {
        uuid id PK
        string email
        string password_hash
        string business_name
        string address
        string tax_id
        string crm_webhook_url
        timestamp created_at
    }

    VEHICLES {
        uuid id PK
        uuid owner_id FK "References USERS or DEALERS"
        string owner_type "USER or DEALER"
        string make
        string model
        int year
        string trim
        int mileage
        string condition
        decimal asking_price
        string status "ACTIVE|SOLD|DRAFT"
        jsonb metadata "Features, service history"
        timestamp created_at
    }

    AUCTIONS {
        uuid id PK
        uuid vehicle_id FK
        string type "FORWARD|REVERSE"
        decimal starting_price
        decimal current_winning_price
        uuid current_winner_id FK "Dealer ID or User ID"
        timestamp start_time
        timestamp end_time
        string status "OPEN|CLOSED|CANCELLED"
    }

    BIDS {
        uuid id PK
        uuid auction_id FK
        uuid bidder_id FK "Dealer ID or User ID"
        string bidder_type "USER or DEALER"
        decimal amount
        timestamp created_at
    }

    TRANSACTIONS {
        uuid id PK
        uuid auction_id FK
        uuid vehicle_id FK
        uuid buyer_id FK
        uuid seller_id FK
        decimal final_price
        string status "PENDING|COMPLETED"
        timestamp completed_at
    }

    CHAT_SESSIONS {
        uuid id PK
        uuid user_id FK
        jsonb messages_history "Full structured LangChain Memory"
        jsonb extracted_criteria "Slot-filled values like Make, Price"
        timestamp last_updated
    }

    USERS ||--o{ VEHICLES : "Sells"
    DEALERS ||--o{ VEHICLES : "Inventories"
    VEHICLES ||--o| AUCTIONS : "Creates"
    AUCTIONS ||--o{ BIDS : "Receives"
    USERS ||--o{ BIDS : "Places (Reverse)"
    DEALERS ||--o{ BIDS : "Places (Forward)"
    AUCTIONS ||--o| TRANSACTIONS : "Results In"
    USERS ||--o{ CHAT_SESSIONS : "Initiates"
```

## Explanation
- A **Vehicle** uses Polymorphic association (`owner_type` and `owner_id`) to belong to either a regular User or a registered Dealer.
- An **Auction** tracks the current state in PostgreSQL. Fast-moving bids will first be tracked in Redis and then asynchronously flushed down to the **Bids** table.
- **ChatSessions** store the conversational history and parsed JSON values (slot-filling data) so that context isn't lost if the user leaves the page or switches devices.
