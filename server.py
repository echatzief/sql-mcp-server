import asyncio
from typing import Optional

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

from src.lib.config import Config
from src.database.manager import DatabaseManager
from src.database.formatter import format_results


def create_mcp_server(database_manager: DatabaseManager, config: Config) -> FastMCP:
    port = int(getattr(config, "http_port", 8080))
    mcp = FastMCP("sql-mcp-server", host=config.db_host, port=port)

    @mcp.tool()
    async def execute_query(query: str, format_type: str = "json") -> str:
        results = await database_manager.client.execute_query(query)
        return format_results(results, format_type)

    @mcp.tool()
    async def list_databases(format_type: str = "json") -> str:
        results = await database_manager.client.list_databases()
        return format_results(results, format_type)

    @mcp.tool()
    async def list_tables(
        database: Optional[str] = None, format_type: str = "json"
    ) -> str:
        results = await database_manager.client.list_tables(database)
        return format_results(results, format_type)

    @mcp.tool()
    async def describe_table(table_name: str, format_type: str = "json") -> str:
        results = await database_manager.client.describe_table(table_name)
        return format_results(results, format_type)

    return mcp


async def run_server():
    config = Config()
    database_manager = DatabaseManager(config)
    await database_manager.connect()

    mcp = create_mcp_server(database_manager, config)
    await mcp.run_streamable_http_async()

    await database_manager.disconnect()


def main():
    asyncio.run(run_server())

