-- MTEJA AI PostgreSQL schema (multi-tenant)
-- Core tables: organizations, users, customers, conversations, messages,
-- leads, deals, campaigns, ai_agents, integrations, audit_logs
-- All tenant-scoped tables include organization_id with proper indexes

CREATE TABLE IF NOT EXISTS stock (
	id BIGSERIAL PRIMARY KEY,
	organization_id BIGINT NOT NULL REFERENCES organizations(id),
	name VARCHAR(255) NOT NULL,
	quantity INTEGER NOT NULL DEFAULT 0 CHECK (quantity >= 0),
	price NUMERIC(12, 2) NOT NULL CHECK (price >= 0),
	class VARCHAR(100) NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_stock_organization_id ON stock (organization_id);
