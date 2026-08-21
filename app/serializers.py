from decimal import Decimal
from typing import Any

import asyncpg


def _convert(value: Any) -> Any:
    if isinstance(value, (bytes, bytearray, memoryview)):
        return "0x" + bytes(value).hex()
    if isinstance(value, Decimal):
        # numeric Wei values overflow float64 — serialize as plain string
        # (format 'f' avoids scientific notation like 1.8E+17)
        return format(value, "f")
    return value


def row_to_dict(row: asyncpg.Record) -> dict[str, Any]:
    return {k: _convert(v) for k, v in row.items()}
