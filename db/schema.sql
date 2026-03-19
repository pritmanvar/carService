-- AI Automotive Platform
-- Initial PostgreSQL Schema Definition

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. USERS
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(20),
    role VARCHAR(20) DEFAULT 'USER' CHECK (role IN ('USER', 'ADMIN')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. DEALERS
CREATE TABLE dealers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    business_name VARCHAR(255) NOT NULL,
    address TEXT,
    tax_id VARCHAR(50),
    crm_webhook_url VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. VEHICLES
CREATE TABLE vehicles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    owner_id UUID NOT NULL,
    owner_type VARCHAR(10) CHECK (owner_type IN ('USER', 'DEALER')),
    make VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    year INT NOT NULL,
    trim VARCHAR(100),
    mileage INT,
    condition VARCHAR(50),
    asking_price DECIMAL(10, 2),
    status VARCHAR(20) DEFAULT 'DRAFT' CHECK (status IN ('DRAFT', 'ACTIVE', 'SOLD')),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. AUCTIONS
CREATE TABLE auctions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vehicle_id UUID REFERENCES vehicles(id) ON DELETE CASCADE,
    type VARCHAR(20) CHECK (type IN ('FORWARD', 'REVERSE')),
    starting_price DECIMAL(10, 2) NOT NULL,
    current_winning_price DECIMAL(10, 2),
    current_winner_id UUID,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR(20) DEFAULT 'OPEN' CHECK (status IN ('OPEN', 'CLOSED', 'CANCELLED'))
);

-- 5. BIDS
CREATE TABLE bids (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    auction_id UUID REFERENCES auctions(id) ON DELETE CASCADE,
    bidder_id UUID NOT NULL,
    bidder_type VARCHAR(10) CHECK (bidder_type IN ('USER', 'DEALER')),
    amount DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 6. TRANSACTIONS
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    auction_id UUID REFERENCES auctions(id) ON DELETE CASCADE,
    vehicle_id UUID REFERENCES vehicles(id),
    buyer_id UUID NOT NULL,
    seller_id UUID NOT NULL,
    final_price DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'COMPLETED', 'CANCELLED')),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Create Indexes for Query Optimisation
CREATE INDEX idx_vehicles_status ON vehicles(status);
CREATE INDEX idx_auctions_status_endtime ON auctions(status, end_time);
CREATE INDEX idx_bids_auction_created ON bids(auction_id, created_at DESC);
CREATE INDEX idx_vehicles_make_model ON vehicles(make, model);
