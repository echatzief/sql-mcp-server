def format_execute_query_description(read_only):
    if read_only:
        return """
            ⚠️ READ-ONLY MODE ⚠️
            This database connection only allows read operations.

            For PostgreSQL/MySQL: Only SELECT, SHOW, DESCRIBE queries allowed.
            WRITE operations (INSERT, UPDATE, DELETE, DROP, CREATE, ALTER) are BLOCKED.

            For MongoDB: Only read operations (find, find_one, aggregate, count) allowed.
            Use JSON format with operation type:
                - find: {"collection": "users", "operation": "find", "filter": {"active": true}, "limit": 10}
                - find_one: {"collection": "users", "operation": "find_one", "filter": {"_id": "..."}}
                - aggregate: {"collection": "users", "operation": "aggregate", "pipeline": [{"$group": {...}}]}
                - count: {"collection": "users", "operation": "count", "filter": {...}}
            WRITE operations (insert_*, update_*, delete_*) are BLOCKED.
            Optional fields for find: projection, sort, skip, limit
        """
    else:
        return """
            Execute a query against the database.

            For PostgreSQL/MySQL: Use SQL syntax (e.g., "SELECT * FROM users WHERE active = true LIMIT 10")

            For MongoDB: Use JSON format with operation type:
                - find: {"collection": "users", "operation": "find", "filter": {"active": true}, "limit": 10}
                - find_one: {"collection": "users", "operation": "find_one", "filter": {"_id": "..."}}
                - insert_one: {"collection": "users", "operation": "insert_one", "document": {"name": "John"}}
                - insert_many: {"collection": "users", "operation": "insert_many", "documents": [{...}, {...}]}
                - update_one/update_many: {"collection": "users", "operation": "update_many", "filter": {...}, "update": {"$set": {...}}}
                - delete_one/delete_many: {"collection": "users", "operation": "delete_many", "filter": {...}}
                - aggregate: {"collection": "users", "operation": "aggregate", "pipeline": [{"$group": {...}}]}
                - count: {"collection": "users", "operation": "count", "filter": {...}}
            Optional fields for find: projection, sort, skip, limit
        """
