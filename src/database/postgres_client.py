from dataclasses import dataclass
from typing import Any

import asyncpg


@dataclass
class PostgresClient:
    pool: asyncpg.Pool

    async def execute_query(self, query: str, params: tuple | None = None) -> list[dict[str, Any]]:
        async with self.pool.acquire() as connection:
            rows = (
                await connection.fetch(query, *params) if params else await connection.fetch(query)
            )
            return [dict(row) for row in rows]

    async def list_databases(self) -> list[str]:
        result = await self.execute_query(
            "SELECT datname FROM pg_database WHERE datistemplate = false"
        )
        return [row["datname"] for row in result]

    async def list_tables(self, database: str | None = None) -> list[str]:
        query = """
            SELECT tablename FROM pg_tables
            WHERE schemaname = 'public'
        """
        result = await self.execute_query(query)
        return [row["tablename"] for row in result]

    async def describe_table(self, table_name: str) -> list[dict[str, Any]]:
        query = """
            SELECT
                column_name,
                data_type,
                is_nullable,
                column_default,
                character_maximum_length
            FROM information_schema.columns
            WHERE table_name = $1
            ORDER BY ordinal_position
        """
        return await self.execute_query(query, (table_name,))

    async def close(self) -> None:
        await self.pool.close()
