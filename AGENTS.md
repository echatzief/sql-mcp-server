# AGENTS.md - Database MCP Server

This file contains important information for AI agents working on this project.

## Project Overview

This is a **Model Context Protocol (MCP) server** that provides database operations as tools for LLM-powered applications. It supports PostgreSQL, MySQL, and MongoDB with connection pooling and flexible result formatting.

## Technology Stack

- **Language**: Python 3.11+
- **Framework**: MCP (Model Context Protocol) via `mcp>=1.26.0`
- **Package Manager**: `uv` (recommended) or `pip`
- **Database Drivers**:
  - PostgreSQL: `asyncpg`
  - MySQL: `aiomysql`
  - MongoDB: `pymongo>=4.16.0`
- **Environment Management**: `python-dotenv`

## Project Structure

```
database-mcp-server/
├── main.py                    # Entry point - just imports and calls main() from src.server
├── pyproject.toml             # Project configuration with uv
├── uv.lock                    # Locked dependencies
├── .env                       # Environment variables (not in git)
├── .env.example               # Example environment variables
├── .python-version            # Python version specification
├── README.md                  # Comprehensive documentation
└── src/
    ├── server.py              # MCP server setup and tool definitions
    ├── lib/
    │   ├── config.py          # Configuration management (reads from env vars)
    │   ├── utils.py           # Utility functions
    │   ├── middleware.py      # Middleware for MCP server
    │   └── mcp.py             # MCP-specific utilities
    └── database/
        ├── manager.py         # Database connection pool manager
        ├── formatter.py       # Result formatting (JSON/Markdown)
        ├── postgres_client.py # PostgreSQL-specific operations
        ├── mysql_client.py    # MySQL-specific operations
        └── mongodb_client.py  # MongoDB-specific operations
```

## Key Files

### 1. `src/server.py`
The main server file that:
- Creates the FastMCP server instance
- Defines 4 tools: `execute_query`, `list_databases`, `list_tables`, `describe_table`
- Sets up HTTP transport via `run_streamable_http_async()`
- Binds to host/port from config (default: 0.0.0.0:8080)

### 2. `src/lib/config.py`
Configuration management that reads from environment variables:
- `DATABASE_PROVIDER`: postgres, mysql, or mongodb
- `DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_USER`, `DATABASE_PASSWORD`, `DATABASE_NAME`
- `DATABASE_MIN_POOL_SIZE`, `DATABASE_MAX_POOL_SIZE`
- `HTTP_HOST`, `HTTP_PORT`

### 3. `src/database/manager.py`
Database connection pool manager that:
- Initializes appropriate client based on DATABASE_PROVIDER
- Manages connection lifecycle (connect/disconnect)
- Delegates operations to provider-specific clients

## Running the Project

```bash
# Install dependencies (using uv - recommended)
uv pip install -e .

# Run the server
uv run python main.py

# Alternative using Python directly
python main.py
```

## Code Style and Linting

- **Formatter**: The project uses `ruff` for linting and formatting (evidenced by `.ruff_cache` directory)
- **No explicit lint script** found in pyproject.toml
- When editing files, run `ruff check .` and `ruff format .` if available
- Follow existing Python code style in the project

## MCP Tools Provided

1. **`execute_query(query, format_type="json")`** - Execute database queries
   - PostgreSQL/MySQL: SQL syntax
   - MongoDB: JSON format with operation type
   
2. **`list_databases(format_type="json")`** - List all databases

3. **`list_tables(database=None, format_type="json")`** - List tables/collections

4. **`describe_table(table_name, format_type="json")`** - Get schema information

## Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# Required
DATABASE_PROVIDER=postgres  # or mysql, mongodb
DATABASE_HOST=localhost
DATABASE_PORT=5432          # 3306 for MySQL, 27017 for MongoDB
DATABASE_USER=your_username
DATABASE_NAME=your_database
DATABASE_MIN_POOL_SIZE=1
DATABASE_MAX_POOL_SIZE=10

# Optional
DATABASE_PASSWORD=your_password
HTTP_HOST=0.0.0.0
HTTP_PORT=8080
```

## Common Development Tasks

### Adding a New Database Provider

1. Create `src/database/{provider}_client.py`
2. Implement the same interface as existing clients:
   - `async def connect()` / `async def disconnect()`
   - `async def execute_query(query)`
   - `async def list_databases()`
   - `async def list_tables(database)`
   - `async def describe_table(table_name)`
3. Update `src/database/manager.py` to include the new provider
4. Update `DATABASE_PROVIDER` validation in `src/lib/config.py`

### Adding a New Tool

1. Add tool decorator in `src/server.py:create_mcp_server()`:
   ```python
   @mcp.tool()
   async def new_tool(param: str) -> str:
       results = await database_manager.client.new_operation(param)
       return format_results(results, "json")
   ```
2. Implement the operation in the appropriate database client

### Modifying Result Format

- Edit `src/database/formatter.py`
- The `format_results()` function handles both "json" and "markdown" formats

## MCP Client Configuration

Clients can connect via:

1. **Stdio transport** (recommended for local use):
   ```json
   {
     "mcpServers": {
       "sql": {
         "command": "uv",
         "args": ["--directory", "/path/to/project", "run", "python", "main.py"]
       }
     }
   }
   ```

2. **HTTP transport**:
   ```json
   {
     "mcpServers": {
       "sql": {
         "url": "http://localhost:8080/mcp"
       }
     }
   }
   ```

## Testing

- No tests are currently implemented (noted in README)
- If adding tests, consider:
  - Unit tests for each database client
  - Integration tests with test databases
  - Mock database connections for CI/CD

## Important Notes

1. **Async Only**: All database operations are async. Never use blocking calls.
2. **Connection Pooling**: The DatabaseManager handles connection pooling automatically.
3. **Format Types**: Tools support "json" and "markdown" output formats.
4. **MongoDB Queries**: Use JSON format with operation field, not raw MongoDB shell syntax.
5. **No Test Suite**: There are currently no automated tests in this project.

## Dependencies to Know

- `mcp>=1.26.0` - MCP framework (FastMCP class)
- `asyncpg>=0.31.0` - PostgreSQL async driver
- `aiomysql>=0.3.2` - MySQL async driver  
- `pymongo>=4.16.0` - MongoDB driver (has both sync and async APIs)
- `python-dotenv>=1.2.1` - Environment variable loading

## Version History

- **v1.1.0** (2026-02-14): Added MongoDB support
- **v1.0.0** (2026-02-05): Initial release with PostgreSQL and MySQL
