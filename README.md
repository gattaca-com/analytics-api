# analytics-api

Read-only FastAPI over the Gattaca `ethereum` warehouse. Exposes three
resources: **mined blocks**, **mined transactions**, and **relay bid
adjustments**.

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
`sql/grants.sql` (SELECT on the three source tables plus two `label` lookup
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
