import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from bson import ObjectId, json_util
from pymongo import AsyncMongoClient


@dataclass
class MongoDBClient:
    client: AsyncMongoClient
    database: str

    async def execute_query(
        self, query_json: str, params: tuple | None = None
    ) -> list[dict[str, Any]]:
        try:
            query = json.loads(query_json)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON query format")

        collection_name = query.get("collection")
        operation = query.get("operation", "find")

        if not collection_name:
            raise ValueError("Collection name is required")

        collection = self.client[self.database][collection_name]

        if operation == "find":
            cursor = collection.find(query.get("filter", {}), query.get("projection"))
            if "sort" in query:
                cursor = cursor.sort(list(query["sort"].items()))
            if "skip" in query:
                cursor = cursor.skip(query["skip"])
            if "limit" in query:
                cursor = cursor.limit(query["limit"])
            return [self._serialize_doc(doc) async for doc in cursor]

        elif operation == "find_one":
            doc = await collection.find_one(query.get("filter", {}), query.get("projection"))
            return [self._serialize_doc(doc)] if doc else []

        elif operation == "aggregate":
            pipeline = query.get("pipeline", [])
            cursor = await collection.aggregate(pipeline)
            docs = await cursor.to_list(length=None)
            return [self._serialize_doc(doc) for doc in docs]

        elif operation == "count":
            count = await collection.count_documents(query.get("filter", {}))
            return [{"count": count}]

        elif operation == "insert_one":
            result = await collection.insert_one(query.get("document", {}))
            return [{"inserted_id": str(result.inserted_id)}]

        elif operation == "insert_many":
            result = await collection.insert_many(query.get("documents", []))
            return [{"inserted_ids": [str(id) for id in result.inserted_ids]}]

        elif operation == "update_one":
            result = await collection.update_one(query.get("filter", {}), query.get("update", {}))
            return [{"matched": result.matched_count, "modified": result.modified_count}]

        elif operation == "update_many":
            result = await collection.update_many(query.get("filter", {}), query.get("update", {}))
            return [{"matched": result.matched_count, "modified": result.modified_count}]

        elif operation == "delete_one":
            result = await collection.delete_one(query.get("filter", {}))
            return [{"deleted": result.deleted_count}]

        elif operation == "delete_many":
            result = await collection.delete_many(query.get("filter", {}))
            return [{"deleted": result.deleted_count}]

        else:
            raise ValueError(f"Unsupported operation: {operation}")

    async def list_databases(self) -> list[str]:
        return await self.client.list_database_names()

    async def list_tables(self, database: str | None = None) -> list[str]:
        db_name = database or self.database
        return await self.client[db_name].list_collection_names()

    async def describe_table(self, collection_name: str) -> list[dict[str, Any]]:
        collection = self.client[self.database][collection_name]

        sample_docs = []
        async for doc in collection.find().limit(100):
            sample_docs.append(doc)

        if not sample_docs:
            return []

        schema = {}

        for doc in sample_docs:
            self._analyze_document(doc, schema)

        result = []
        for field_name, field_info in sorted(schema.items()):
            result.append(
                {
                    "field_name": field_name,
                    "types_found": list(field_info["types"]),
                    "sample_values": field_info["samples"][:3],
                    "nullable": True,
                    "document_count": len(sample_docs),
                }
            )

        return result

    async def close(self) -> None:
        await self.client.close()

    def _analyze_document(self, doc: dict, schema: dict, parent_key: str = ""):
        for key, value in doc.items():
            full_key = f"{parent_key}.{key}" if parent_key else key

            if full_key not in schema:
                schema[full_key] = {"types": set(), "samples": []}

            value_type = type(value).__name__
            schema[full_key]["types"].add(value_type)

            if len(schema[full_key]["samples"]) < 5:
                schema[full_key]["samples"].append(self._serialize_value(value))

            if isinstance(value, dict):
                self._analyze_document(value, schema, full_key)

    def _serialize_doc(self, doc: dict) -> dict:
        return json.loads(json_util.dumps(doc))

    def _serialize_value(self, value) -> Any:
        if isinstance(value, ObjectId):
            return str(value)
        elif isinstance(value, datetime):
            return value.isoformat()
        elif isinstance(value, dict):
            return {k: self._serialize_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._serialize_value(v) for v in value]
        return value
