# analytics-api

Read-only FastAPI over the Gattaca `ethereum` warehouse. Exposes mined
blocks, mined transactions, relay bid adjustments / winning bids / delivered
payloads, Titan builder submitted blocks, and orderflow transaction sources.

Interactive docs (OpenAPI/Swagger) are auto-generated:

- Swagger UI: `http://<host>:8000/docs`
- ReDoc: `http://<host>:8000/redoc`
- OpenAPI JSON: `http://<host>:8000/openapi.json`

## Conventions

- **Hashes / addresses** — returned and accepted as `0x`-hex strings.
- **Wei values** (`numeric(78,0)`) — returned as **decimal strings** (they
  overflow JSON floats).
- **Timestamps** — ISO-8601 (`TIMESTAMPTZ`).
- Every list endpoint requires **exactly one selector**: a point lookup
  (`slot` / `block` / `hash`) **or** a `start`+`end` timestamp range.
- Ranges are capped at `MAX_RANGE_SECONDS` (default 6h) to protect the
  TimescaleDB hypertables.

## Endpoints

| Method | Path | Selectors | Range column |
|--------|------|-----------|--------------|
| GET | `/blocks` | `slot`, `block`, `hash`, `start`+`end` | `timestamp` |
| GET | `/transactions` | `hash`, `block`, `start`+`end` | `timestamp` |
| GET | `/bid-adjustments` | `slot`, `block`, `hash`, `start`+`end` | `submitted_received_at` |
| GET | `/winning-bids` | `slot`, `hash`, `start`+`end` | `winning_timestamp` |
| GET | `/delivered-payloads` | `slot`, `block`, `hash` (no range — no timestamp column) | — |
| GET | `/submitted-blocks` | `slot`, `uuid`, `start`+`end` | `submission_ts` |
| GET | `/transaction-sources` | `hash`, `bundle`, `start`+`end` | `timestamp` |
| GET | `/health` | — | — |

### Pagination

All list endpoints accept `limit` (default 100, max 1000) and `offset`.
Responses are enveloped:

```json
{
  "data": [ ... ],
  "pagination": { "limit": 100, "offset": 0, "count": 100, "has_more": true }
}
```

### Rate limits

Requests are rate-limited per client IP: `RATE_LIMIT_PER_MINUTE` (default
120/min). On 429 the response carries a `Retry-After` header —
clients (including coding agents) should honour it and back off. Successful
responses include `X-RateLimit-Limit` / `X-RateLimit-Remaining`. Set a limit
to `0` to disable it.

### Examples

```bash
curl 'http://localhost:8000/blocks?slot=9000000'
curl 'http://localhost:8000/transactions?block=20000000&limit=50'
curl 'http://localhost:8000/bid-adjustments?start=2026-08-18T10:00:00Z&end=2026-08-18T11:00:00Z'
```

## Configuration

Copy `.env.example` to `.env` and fill in the `api_ro` credentials. See
`app/config.py` for all knobs (pool size, limits, range cap, statement
timeout).

## Database access

The API connects as a dedicated read-only role with the minimum grants in
`sql/grants.sql` (SELECT on the source tables plus the `label` lookup
tables). No write access, no `ALTER DEFAULT PRIVILEGES`.

## Run

```bash
# local
pip install -r requirements.txt
uvicorn app.main:app --reload

# docker
docker compose up --build -d
```

Runs on port 8000 (host networking), separate from bundle-analytics (5000).
For higher throughput add `--workers N` to the uvicorn command.
