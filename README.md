# SQL-MCP-Server

A Model Context Protocol (MCP) server that provides SQL database operations as tools for LLM-powered applications. Supports PostgreSQL and MySQL databases with connection pooling and flexible result formatting.

## Features

- **Multi-database support**: PostgreSQL and MySQL
- **Connection pooling**: Efficient database connection management
- **Multiple result formats**: JSON and Markdown table output
- **Streamable HTTP**: Modern MCP transport via HTTP
- **Async operations**: Full async/await support for non-blocking database queries

## Tools

| Tool | Description |
|------|-------------|
| `execute_query` | Execute arbitrary SQL queries against the database |
| `list_databases` | List all available databases |
| `list_tables` | List all tables in a database (defaults to configured database) |
| `describe_table` | Get schema information for a specific table |

## Requirements

- Python 3.11+
- PostgreSQL 12+ or MySQL 8.0+

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd sql-mcp-server

# Install dependencies using uv (recommended)
uv pip install -e .

# Or using pip
pip install -e .
```

## Configuration

Copy `.env.example` to `.env` and configure the environment variables:

```bash
cp .env.example .env
```

Then edit `.env` with your database credentials and settings:

```env
# Database Configuration
DATABASE_PROVIDER=postgres  # or mysql
DATABASE_HOST=localhost
DATABASE_PORT=5432          # 3306 for MySQL
DATABASE_USER=your_username
DATABASE_PASSWORD=your_password
DATABASE_NAME=your_database
DATABASE_MIN_POOL_SIZE=1
DATABASE_MAX_POOL_SIZE=10

# Server Configuration (optional)
HTTP_HOST=0.0.0.0          # Bind address (defaults to all interfaces)
HTTP_PORT=8080
```

### Configuration Options

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_PROVIDER` | Yes | - | Database provider: `postgres` or `mysql` |
| `DATABASE_HOST` | Yes | - | Database server hostname or IP |
| `DATABASE_PORT` | Yes | - | Database server port (5432 for PostgreSQL, 3306 for MySQL) |
| `DATABASE_USER` | Yes | - | Database username |
| `DATABASE_PASSWORD` | No | - | Database password |
| `DATABASE_NAME` | Yes | - | Default database to connect to |
| `DATABASE_MIN_POOL_SIZE` | Yes | - | Minimum pool size for connections |
| `DATABASE_MAX_POOL_SIZE` | Yes | - | Maximum pool size for connections |
| `HTTP_HOST` | No | `0.0.0.0` | HTTP server bind address |
| `HTTP_PORT` | No | 8080 | HTTP server port for MCP |

## Usage

### Running the Server

```bash
# Using uv (recommended)
uv run python main.py

# Using Python directly
python main.py
```

### MCP Client Configuration

Add the server to your MCP client configuration:

**Using uv (recommended for dependency isolation):**

```json
{
  "mcpServers": {
    "sql": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/sql-mcp-server",
        "run",
        "python",
        "main.py"
      ]
    }
  }
}
```

**Using Python directly:**

```json
{
  "mcpServers": {
    "sql": {
      "command": "python",
      "args": ["/path/to/sql-mcp-server/main.py"]
    }
  }
}
```

**Direct HTTP Connection:**

The server exposes a Streamable HTTP endpoint. Configure your MCP client to connect directly:

```json
{
  "mcpServers": {
    "sql": {
      "url": "http://localhost:8080/mcp"
    }
  }
}
```

> **Note**: For direct HTTP connections, ensure the server is running and accessible at the specified URL.

### Example Tool Calls

```python
# List all databases
list_databases()

# List tables in the configured database
list_tables()

# List tables in a specific database
list_tables(database="another_db")

# Describe a table schema
describe_table("users")

# Execute a custom query
execute_query("SELECT * FROM users WHERE active = true LIMIT 10")

# Get results in Markdown format
execute_query("SELECT name, email FROM users", format_type="markdown")
```

## Project Structure

```
sql-mcp-server/
├── main.py                 # Entry point
├── server.py               # MCP server and tool definitions
├── pyproject.toml          # Project configuration
├── .env                    # Environment variables (create this)
└── src/
    ├── lib/
    │   ├── config.py       # Configuration management
    │   └── utils.py        # Utility functions
    └── database/
        ├── manager.py      # Database connection pool manager
        ├── formatter.py    # Result formatting (JSON/Markdown)
        ├── postgres_client.py  # PostgreSQL-specific operations
        └── mysql_client.py     # MySQL-specific operations
```

## Development

```bash
# Run in development mode with auto-reload (requires watching tool)
uv run watch -c "python main.py" .
```

## Dependencies

| Package | Purpose |
|---------|---------|
| `mcp>=1.26.0` | Model Context Protocol framework |
| `asyncpg` | PostgreSQL async driver |
| `aiomysql` | MySQL async driver |
| `python-dotenv` | Environment variable management |

## Running Tests

Tests are not yet implemented.

## License

MIT

## Changelog

### v0.1.0 (2026-02-05)

- Initial release
- Added Streamable HTTP transport support for MCP
- Separated HTTP host configuration into dedicated environment variable
- Added comprehensive README documentation
- Improved server module organization (moved server.py to src/server.py)
- Added example .env configuration file
