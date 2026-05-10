import sqlite3
import asyncio
from functools import lru_cache


@lru_cache(maxsize=1)
def _build_mock_db() -> sqlite3.Connection:
    """Build an in-memory SQLite analytics database (singleton)."""
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.executescript("""
        CREATE TABLE sales (
            id      INTEGER PRIMARY KEY,
            product TEXT,
            revenue REAL,
            units   INTEGER,
            month   TEXT
        );
        INSERT INTO sales VALUES
            (1, 'Widget Pro',  15000.50, 120, '2024-01'),
            (2, 'Widget Pro',  18200.00, 145, '2024-02'),
            (3, 'Widget Pro',  21000.00, 168, '2024-03'),
            (4, 'Gadget X',     8500.00,  85, '2024-01'),
            (5, 'Gadget X',     9200.00,  92, '2024-02'),
            (6, 'Gadget X',    11000.00, 110, '2024-03'),
            (7, 'SuperTool',   22000.00,  55, '2024-01'),
            (8, 'SuperTool',   25500.00,  63, '2024-02'),
            (9, 'SuperTool',   28000.00,  70, '2024-03');

        CREATE TABLE users_analytics (
            id           INTEGER PRIMARY KEY,
            region       TEXT,
            active_users INTEGER,
            new_signups  INTEGER,
            month        TEXT
        );
        INSERT INTO users_analytics VALUES
            (1, 'North America', 12500, 340, '2024-01'),
            (2, 'Europe',         8900, 210, '2024-01'),
            (3, 'Asia Pacific',   6700, 189, '2024-01'),
            (4, 'North America', 13200, 380, '2024-02'),
            (5, 'Europe',         9400, 225, '2024-02'),
            (6, 'Asia Pacific',   7100, 201, '2024-02');
    """)
    return conn


async def query_database(sql_query: str) -> str:
    """Execute a read-only SELECT query on the mock analytics database."""
    if not sql_query.strip().upper().startswith("SELECT"):
        return "❌ Only SELECT queries are permitted."

    loop = asyncio.get_event_loop()

    def _run():
        conn = _build_mock_db()
        try:
            cursor = conn.execute(sql_query)
            rows = cursor.fetchall()
            columns = [d[0] for d in cursor.description]
            if not rows:
                return "Query returned no results."
            col_widths = [max(len(c), max(len(str(r[i])) for r in rows)) for i, c in enumerate(columns)]
            header = " | ".join(c.ljust(col_widths[i]) for i, c in enumerate(columns))
            sep = "-+-".join("-" * w for w in col_widths)
            body = "\n".join(
                " | ".join(str(row[i]).ljust(col_widths[i]) for i in range(len(columns)))
                for row in rows
            )
            return f"```\n{header}\n{sep}\n{body}\n```"
        except Exception as exc:
            return f"❌ Query error: {exc}"

    return await loop.run_in_executor(None, _run)
