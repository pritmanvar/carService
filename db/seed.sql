-- Seed script for local development and testing

-- Seed Users
INSERT INTO users (id, email, password_hash, first_name, last_name, phone, role) VALUES 
('11111111-1111-1111-1111-111111111111', 'seller@example.com', 'hashed_pw', 'John', 'Doe', '555-0100', 'USER'),
('22222222-2222-2222-2222-222222222222', 'buyer@example.com', 'hashed_pw', 'Jane', 'Smith', '555-0101', 'USER');

-- Seed Dealers
INSERT INTO dealers (id, email, password_hash, business_name, address, tax_id) VALUES 
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'dealer1@example.com', 'hashed_pw', 'Prime Motors', '123 Auto Row', 'TAX123'),
('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'dealer2@example.com', 'hashed_pw', 'City Cars LLC', '456 Dealership Bay', 'TAX456');

-- Seed Vehicles
INSERT INTO vehicles (id, owner_id, owner_type, make, model, year, trim, mileage, condition, asking_price, status) VALUES 
('33333333-3333-3333-3333-333333333333', '11111111-1111-1111-1111-111111111111', 'USER', 'Tesla', 'Model 3', 2022, 'Long Range', 15000, 'Excellent', NULL, 'ACTIVE'),
('44444444-4444-4444-4444-444444444444', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'DEALER', 'Ford', 'F-150', 2021, 'Lariat', 30000, 'Good', 45000, 'ACTIVE');

-- Seed Auctions
-- Forward Auction (User Selling Tesla)
INSERT INTO auctions (id, vehicle_id, type, starting_price, start_time, end_time, status) VALUES 
('55555555-5555-5555-5555-555555555555', '33333333-3333-3333-3333-333333333333', 'FORWARD', 30000.00, NOW() - INTERVAL '1 day', NOW() + INTERVAL '2 days', 'OPEN');

-- Dummy Bids
INSERT INTO bids (id, auction_id, bidder_id, bidder_type, amount) VALUES 
('66666666-6666-6666-6666-666666666666', '55555555-5555-5555-5555-555555555555', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'DEALER', 31000.00),
('77777777-7777-7777-7777-777777777777', '55555555-5555-5555-5555-555555555555', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'DEALER', 32500.00);

-- Update the highest bid back in the auction table
UPDATE auctions SET current_winning_price = 32500.00, current_winner_id = 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb' WHERE id = '55555555-5555-5555-5555-555555555555';
