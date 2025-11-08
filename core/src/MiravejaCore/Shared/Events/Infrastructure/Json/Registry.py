import json
import os
from functools import lru_cache
from typing import Any, Dict

from MiravejaCore.Shared.Events.Domain.Configuration import KafkaConfig
from MiravejaCore.Shared.Events.Domain.Exceptions import (
    InvalidSchemaJSONError,
    SchemaFileNotFoundError,
    SchemasDirectoryNotFoundError,
)
from MiravejaCore.Shared.Events.Domain.Interfaces import ISchemaRegistry


class JsonSchemaRegistry(ISchemaRegistry):
    """Registry for managing JSON schemas for events."""

    def __init__(self, config: KafkaConfig):
        self._config = config

    @lru_cache(maxsize=128)
    def _LoadSchemaFromFile(self, eventType: str, eventVersion: int) -> Dict[str, Any]:
        topicName = self._config.GetTopicName(eventType, eventVersion)
        schemasDir = self._config.eventSchemasPath
        schemaFilePath = os.path.join(schemasDir, f"{topicName}.json")

        if not os.path.exists(schemaFilePath):
            raise SchemasDirectoryNotFoundError(schemaFilePath)

        try:
            with open(schemaFilePath, "r", encoding="utf-8") as schemaFile:
                schema = json.load(schemaFile)
                return schema
        except FileNotFoundError as e:
            raise SchemaFileNotFoundError(schemaFilePath) from e
        except json.JSONDecodeError as e:
            raise InvalidSchemaJSONError(schemaFilePath, e.msg) from e

    async def GetSchema(self, eventType: str, eventVersion: int) -> Dict[str, Any]:
        """Retrieve the schema for a given event type and version."""
        return self._LoadSchemaFromFile(eventType, eventVersion)

    async def RegisterSchema(self, eventType: str, schema: Dict[str, Any]) -> None:
        """Register a new schema for a given event type."""
        topicName = self._config.GetTopicName(eventType, schema.get("version", 1))
        schemasDir = self._config.eventSchemasPath
        schemaFilePath = os.path.join(schemasDir, f"{topicName}.json")

        os.makedirs(schemasDir, exist_ok=True)

        try:
            with open(schemaFilePath, "w", encoding="utf-8") as schemaFile:
                json.dump(schema, schemaFile, indent=4)
        except Exception as e:
            raise InvalidSchemaJSONError(schemaFilePath, str(e)) from e
        # Invalidate the cache for the newly registered schema
        self._LoadSchemaFromFile.cache_clear()
