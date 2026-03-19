# Redis Data Structures for Live Auction State

Because relational databases (PostgreSQL) are too slow to manage high-volume, concurrent reads and writes for live bidding engines, Redis is utilized as an in-memory data grid.

## 1. Pub/Sub Channels
- **`channel:auction:live:{auction_id}`**
  - **Purpose**: Broadcasts new bids instantly to all WebSocket clients (Subscribers) viewing a specific auction.
  - **Payload Structure**:
    ```json
    {
       "event": "NEW_BID",
       "auction_id": "uuid",
       "bid_id": "uuid",
       "bidder_id": "uuid",
       "amount": 45000,
       "timestamp": "2026-03-18T14:30:00Z"
    }
    ```

## 2. Active Auction State (Redis Hashes)
For every currently active auction, a Redis Hash is maintained in memory. It holds the core auction rules and exact current state.
- **Key**: `auction:state:{auction_id}`
- **Type**: Hash (`HSET`)
- **Fields**:
  - `status`: "OPEN"
  - `type`: "FORWARD" | "REVERSE"
  - `end_time`: 1710777600 (Unix timestamp)
  - `starting_price`: 20000
  - `highest_bid_amount` (or `lowest_bid_amount` if Reverse): 25500
  - `winning_bidder_id`: "dealer-uuid-123"
  - `lock`: "0" (Used for distributed locking during bid processing)

## 3. Real-Time Bid Ledger (Sorted Sets)
To allow instant retrieval of the bid history for a new user joining the socket room, Redis maintains the bid list in memory.
- **Key**: `auction:bids:{auction_id}`
- **Type**: Sorted Set (`ZADD`)
- **Score**: Bid Amount (or Timestamp)
- **Member**: JSON String containing Bidder ID and Timestamp.
- *Reasoning*: Sorted Sets (`ZREVRANGE`) allow the server to instantly serve the top 10 highest bids without querying PostgreSQL.

## 4. Anti-Sniping Expiring Keys
To track an anti-sniping extension (if a bid occurs in the last 5 minutes, extend by 5 minutes):
- When a bid is placed, the backend checks `HGET auction:state:end_time`.
- If `end_time` - `current_time` < 300s, it updates the `end_time` by adding 300s.
- It then issues a `PUBLISH channel:auction:live:{auction_id}` with `event: "TIMER_EXTENDED"`.

## 5. Session Caching
- **Key**: `session:{jwt_token}`
- **Type**: String (with TTL)
- Keeps user authentication instantly verifiable by the WebSocket gateway without hitting PostgreSQL.
