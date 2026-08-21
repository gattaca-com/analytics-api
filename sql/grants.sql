-- Minimal read-only grants for the analytics-api role.
-- Run as a superuser against the `ethereum` database.
-- (Reference only — the role was provisioned separately.)

-- CREATE ROLE api_ro LOGIN PASSWORD '<set-me>';

GRANT CONNECT ON DATABASE ethereum TO api_ro;

GRANT USAGE ON SCHEMA mined, relay, builder, orderflow, label TO api_ro;

GRANT SELECT ON mined.block                    TO api_ro;
GRANT SELECT ON mined.transaction              TO api_ro;
GRANT SELECT ON relay.bid_adjustment           TO api_ro;
GRANT SELECT ON relay.winning_bid              TO api_ro;
GRANT SELECT ON relay.delivered_payload        TO api_ro;
GRANT SELECT ON relay.bid_submission           TO api_ro;
GRANT SELECT ON builder.submitted_block        TO api_ro;
GRANT SELECT ON orderflow.transaction_source   TO api_ro;

-- Needed to resolve ids/addresses to human-readable names.
GRANT SELECT ON label.relay                  TO api_ro;  -- relay_id
GRANT SELECT ON label.builder_pubkey         TO api_ro;  -- builder_pubkey_id
GRANT SELECT ON label.address                TO api_ro;  -- blocks: builder / proposer address
GRANT SELECT ON label.builder                TO api_ro;  -- submitted blocks: builder_id
GRANT SELECT ON label.strategy               TO api_ro;  -- submitted blocks: strategy_id
GRANT SELECT ON label.block_type             TO api_ro;  -- submitted blocks: block_type
GRANT SELECT ON label.block_rejection_reason TO api_ro;  -- submitted blocks: removed_reason
GRANT SELECT ON label.entry_point            TO api_ro;  -- transaction sources
GRANT SELECT ON label.source                 TO api_ro;  -- transaction sources
GRANT SELECT ON label.region                 TO api_ro;  -- transaction sources

-- Intentionally NO 'ALTER DEFAULT PRIVILEGES': new tables are not auto-exposed.
