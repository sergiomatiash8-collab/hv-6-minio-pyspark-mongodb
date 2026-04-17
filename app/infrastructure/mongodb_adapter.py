"""
MongoDB adapter with error handling and retry logic.
"""

import time
from typing import List, Dict
from pymongo import MongoClient, UpdateOne
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import structlog
from app.core.exceptions import StorageError

logger = structlog.get_logger()

class MongoDBAdapter:
    def __init__(self, connection_string: str, database: str):
        self.connection_string = connection_string
        self.database_name = database
        self.client = None
        self.db = None
        self._connect()

    def _connect(self, max_retries: int = 3):
        """Connect to MongoDB with retry logic."""
        for attempt in range(max_retries):
            try:
                self.client = MongoClient(
                    self.connection_string,
                    serverSelectionTimeoutMS=5000,
                    connectTimeoutMS=5000
                )
                # Test connection
                self.client.admin.command('ping')
                self.db = self.client[self.database_name]
                
                logger.info("mongodb_connected", 
                            database=self.database_name)
                return
            except (ConnectionFailure, ServerSelectionTimeoutError) as e:
                logger.warning("mongodb_connection_retry", 
                               attempt=attempt + 1, 
                               max_retries=max_retries, 
                               error=str(e))
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise StorageError(f"MongoDB connection failed: {e}")

    def insert_many(self, collection: str, documents: List[Dict]):
        """Insert multiple documents with error handling."""
        if not documents:
            return None
            
        try:
            result = self.db[collection].insert_many(documents)
            logger.info("mongodb_insert_success", 
                        collection=collection, 
                        count=len(documents), 
                        inserted_ids=len(result.inserted_ids))
            return result
        except Exception as e:
            logger.error("mongodb_insert_failed", 
                         collection=collection, 
                         error=str(e))
            raise StorageError(f"Failed to insert documents: {e}")

    def bulk_upsert(self, collection: str, documents: List[Dict], key_field: str):
        """Bulk upsert documents (update or insert)."""
        if not documents:
            return None

        try:
            operations = [
                UpdateOne(
                    {key_field: doc[key_field]},
                    {"$set": doc},
                    upsert=True
                )
                for doc in documents
            ]
            result = self.db[collection].bulk_write(operations)
            
            logger.info("mongodb_bulk_upsert_success", 
                        collection=collection, 
                        matched=result.matched_count, 
                        modified=result.modified_count, 
                        upserted=result.upserted_count)
            return result
        except Exception as e:
            logger.error("mongodb_bulk_upsert_failed", 
                         collection=collection, 
                         error=str(e))
            raise StorageError(f"Bulk upsert failed: {e}")

    def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("mongodb_connection_closed")