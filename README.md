# Database-MCP-Server

A Model Context Protocol (MCP) server that provides database operations as tools for LLM-powered applications. Supports PostgreSQL, MySQL, and MongoDB databases with connection pooling and flexible result formatting.

## Features

- **Multi-database support**: PostgreSQL, MySQL, and MongoDB
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
- PostgreSQL 12+, MySQL 8.0+, or MongoDB 4.0+

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd database-mcp-server

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
DATABASE_PROVIDER=postgres  # or mysql, mongodb
DATABASE_HOST=localhost
DATABASE_PORT=5432          # 3306 for MySQL, 27017 for MongoDB
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
| `DATABASE_PROVIDER` | Yes | - | Database provider: `postgres`, `mysql`, or `mongodb` |
| `DATABASE_HOST` | Yes | - | Database server hostname or IP |
| `DATABASE_PORT` | Yes | - | Database server port (5432 for PostgreSQL, 3306 for MySQL, 27017 for MongoDB) |
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
        "/path/to/database-mcp-server",
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
      "args": ["/path/to/database-mcp-server/main.py"]
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

#### Common Examples (All Providers)

```python
# List all databases
list_databases()

# List tables/collections in the configured database
list_tables()

# List tables/collections in a specific database
list_tables(database="another_db")

# Describe a table/collection schema
describe_table("users")
```

#### PostgreSQL / MySQL Examples (SQL)

For PostgreSQL and MySQL, use standard SQL syntax:

```python
# Execute a SELECT query
execute_query("SELECT * FROM users WHERE active = true LIMIT 10")

# Execute with specific columns
execute_query("SELECT name, email FROM users WHERE age > 18")

# Get results in Markdown format
execute_query("SELECT name, email FROM users", format_type="markdown")

# INSERT, UPDATE, DELETE queries
execute_query("INSERT INTO users (name, email) VALUES ('John', 'john@example.com')")
execute_query("UPDATE users SET status = 'active' WHERE status = 'pending'")
execute_query("DELETE FROM users WHERE inactive = true")

# Join queries
execute_query("""
    SELECT u.name, o.order_id 
    FROM users u 
    JOIN orders o ON u.id = o.user_id 
    WHERE u.active = true
""")
```

#### MongoDB Examples (JSON)

For MongoDB, queries use JSON format with operation type:

```python
# Find documents
execute_query('{"collection": "users", "operation": "find", "filter": {"active": true}, "limit": 10}')

# Find with projection (select specific fields)
execute_query('{"collection": "users", "operation": "find", "projection": {"name": 1, "email": 1}}')

# Find with sorting and pagination
execute_query('{"collection": "users", "operation": "find", "filter": {"active": true}, "sort": {"created_at": -1}, "skip": 0, "limit": 20}')

# Find one document
execute_query('{"collection": "users", "operation": "find_one", "filter": {"_id": "64f8a2b1c9d8e7f6a5b4c3d2"}}')

# Insert a document
execute_query('{"collection": "users", "operation": "insert_one", "document": {"name": "John", "email": "john@example.com", "created_at": "2024-01-15T10:30:00"}}')

# Insert multiple documents
execute_query('{"collection": "users", "operation": "insert_many", "documents": [{"name": "John"}, {"name": "Jane"}]}')

# Update documents
execute_query('{"collection": "users", "operation": "update_one", "filter": {"email": "john@example.com"}, "update": {"$set": {"status": "active"}}}')
execute_query('{"collection": "users", "operation": "update_many", "filter": {"status": "pending"}, "update": {"$set": {"status": "active"}}}')

# Delete documents
execute_query('{"collection": "users", "operation": "delete_one", "filter": {"email": "john@example.com"}}')
execute_query('{"collection": "users", "operation": "delete_many", "filter": {"inactive": true}}')

# Aggregation pipeline
execute_query('{"collection": "orders", "operation": "aggregate", "pipeline": [{"$group": {"_id": "$status", "count": {"$sum": 1}}}]}')

# Count documents
execute_query('{"collection": "users", "operation": "count", "filter": {"active": true}}')
```

**Supported MongoDB Operations:**

| Operation | Description |
|-----------|-------------|
| `find` | Query documents with optional filter, projection, sort, skip, limit |
| `find_one` | Query a single document by filter |
| `insert_one` | Insert a single document |
| `insert_many` | Insert multiple documents |
| `update_one` | Update a single document matching filter |
| `update_many` | Update multiple documents matching filter |
| `delete_one` | Delete a single document matching filter |
| `delete_many` | Delete multiple documents matching filter |
| `aggregate` | Run aggregation pipeline |
| `count` | Count documents matching filter |

**Query Format Reference:**

```json
{
  "collection": "collection_name",    // Required: Collection to query
  "operation": "find",                 // Required: Operation type (see above)
  "filter": {},                        // Optional: Query filter (MongoDB query syntax)
  "projection": {},                    // Optional: Fields to include/exclude
  "sort": {"field": 1},               // Optional: Sort order (1=asc, -1=desc)
  "skip": 0,                           // Optional: Number of documents to skip
  "limit": 10,                         // Optional: Maximum documents to return
  "document": {},                      // For insert_one: Document to insert
  "documents": [{}, {}],               // For insert_many: Array of documents
  "update": {"$set": {}},             // For update operations: Update operators
  "pipeline": [{}, {}]                 // For aggregate: Aggregation pipeline stages
}
```

## Project Structure

```
database-mcp-server/
├── main.py                 # Entry point
├── pyproject.toml          # Project configuration
├── .env                    # Environment variables (create this)
└── src/
    ├── server.py           # MCP server and tool definitions
    ├── lib/
    │   ├── config.py       # Configuration management
    │   ├── utils.py        # Utility functions
    │   ├── middleware.py   # Middleware for MCP server
    │   └── mcp.py          # MCP-specific utilities
    └── database/
        ├── manager.py      # Database connection pool manager
        ├── formatter.py    # Result formatting (JSON/Markdown)
        ├── postgres_client.py  # PostgreSQL-specific operations
        ├── mysql_client.py     # MySQL-specific operations
        └── mongodb_client.py   # MongoDB-specific operations
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
| `pymongo>=4.9.0` | MongoDB async driver |
| `python-dotenv` | Environment variable management |

## Running Tests

Tests are not yet implemented.

## License

MIT

## Changelog

### v1.2.0 (2026-02-19)

- Added MCP middleware support (`src/lib/middleware.py`)
- Added MCP utilities module (`src/lib/mcp.py`)
- Added ruff code formatter and linter configuration

### v1.1.0 (2026-02-14)

- Added MongoDB support with PyMongo async driver
- New `mongodb_client.py` with full CRUD operations (find, insert, update, delete, aggregate, count)
- Schema inference for `describe_table` via document sampling
- Connection pooling support for MongoDB
- Updated documentation with provider-specific examples

### v1.0.0 (2026-02-05)

- Initial release
- Added Streamable HTTP transport support for MCP
- Separated HTTP host configuration into dedicated environment variable
- Added comprehensive README documentation
- Improved server module organization (moved server.py to src/server.py)
- Added example .env configuration file
