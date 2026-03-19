# Migration Strategy & Database Version Control

This document mandates how database schemas will evolve without downtown and how seed data is managed across different environments.

## 1. Migration Tooling
- We will adopt **Alembic** since **SQLAlchemy** is the chosen ORM.
- All SQL modifications MUST be captured in sequential Alembic migration scripts. Directly editing the database in production is strictly prohibited.

## 2. Local Environment Seeding
- The repository contains `/db/seed.sql` which populates dummy users, dealers, active auctions, and bids.
- Developers boot their local databases using Docker Compose (`docker-compose up -d db redis`), which maps `/db/schema.sql` and `/db/seed.sql` to `/docker-entrypoint-initdb.d/` to ensure immediate readiness.

## 3. Staging and UAT Data Strategy
- Staging environments will be seeded with an anonymised sub-set of production-like data to ensure performance and pagination test validity.
- Sensitive PII (emails, names, phone numbers) must be scrambled using Faker scripts prior to dumping into Staging.

## 4. Production Rollout (Zero-Downtime Strategy)
If destructive changes are required (e.g., dropping a column, renaming a field), a phased approach will be used:
1. **Phase 1 (Expand)**: Add the new column/table alongside existing schemas without modifying application code logic.
2. **Phase 2 (Dual Write)**: Update the microservices to write to both the old schema and the new schema. Run a background script to backfill existing data into the new schema.
3. **Phase 3 (Migrate Read)**: Switch microservice read logic to consume data from the new schema only.
4. **Phase 4 (Contract)**: Drop the old schema references.

## 5. Rollback Plans
- Every active migration (`V2__Add_Trim_Column.sql`) must have a corresponding Undo script (`U2__Drop_Trim_Column.sql`).
- During CI/CD execution, a `before-migration` snapshot is created in Amazon RDS to allow an immediate point-in-time recovery if an indexing or locking issue occurs.
