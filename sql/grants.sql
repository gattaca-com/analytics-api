-- Minimal read-only grants for the analytics-api role.
-- Run as a superuser against the `ethereum` database.
-- (Reference only — the role was provisioned separately.)

-- CREATE ROLE api_ro LOGIN PASSWORD '<set-me>';

GRANT CONNECT ON DATABASE ethereum TO api_ro;

GRANT USAGE ON SCHEMA mined, relay, label TO api_ro;

GRANT SELECT ON mined.block          TO api_ro;
GRANT SELECT ON mined.transaction    TO api_ro;
GRANT SELECT ON relay.bid_adjustment TO api_ro;

-- Needed to resolve ids/addresses to human-readable names.
GRANT SELECT ON label.relay          TO api_ro;  -- bid adjustments: relay_id
GRANT SELECT ON label.builder_pubkey TO api_ro;  -- bid adjustments: builder_pubkey_id
GRANT SELECT ON label.address        TO api_ro;  -- blocks: builder / proposer address

-- Intentionally NO 'ALTER DEFAULT PRIVILEGES': new tables are not auto-exposed.
