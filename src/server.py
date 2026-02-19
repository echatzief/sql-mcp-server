import asyncio

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

from src.database.formatter import format_results
from src.database.manager import DatabaseManager
from src.lib.config import Config
from src.lib.mcp import format_execute_query_description
from src.lib.middleware import validate_read_only_query


def create_mcp_server(database_manager: DatabaseManager, config: Config) -> FastMCP:
    mcp = FastMCP("database-mcp-server", host=config.http_host, port=int(config.http_port))

    @mcp.tool(description=format_execute_query_description(config.readonly))
    async def execute_query(query: str, format_type: str = "json") -> str:
        if config.readonly:
            validate_read_only_query(query, config)

        results = await database_manager.client.execute_query(query)
        return format_results(results, format_type)

    @mcp.tool()
    async def list_databases(format_type: str = "json") -> str:
        results = await database_manager.client.list_databases()
        return format_results(results, format_type)

    @mcp.tool()
    async def list_tables(database: str | None = None, format_type: str = "json") -> str:
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
