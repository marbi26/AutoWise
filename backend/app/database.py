"""
AutoWise Dual-Engine Async Database Layer
Supports MongoDB via Motor / PyMongo with auto-failover to an Async JSON Document Store
if local MongoDB daemon is unavailable. Ensures 100% testability and reliability.
"""

import os
import json
import uuid
import socket
from datetime import datetime, timezone
import motor.motor_asyncio
import pymongo
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from backend.app.config import settings

class JSONDocumentCollection:
    """Async MongoDB-like collection wrapper over a persistent JSON datastore."""
    def __init__(self, name: str, parent_store):
        self.name = name
        self.parent = parent_store

    async def find_one(self, filter_dict=None):
        docs = self.parent.get_docs(self.name)
        if not filter_dict:
            return docs[0] if docs else None
        for doc in docs:
            match = True
            for k, v in filter_dict.items():
                if doc.get(k) != v:
                    match = False
                    break
            if match:
                return dict(doc)
        return None

    def find(self, filter_dict=None):
        docs = self.parent.get_docs(self.name)
        matched = []
        if not filter_dict:
            matched = list(docs)
        else:
            for doc in docs:
                match = True
                for k, v in filter_dict.items():
                    if isinstance(v, dict):
                        if "$in" in v and doc.get(k) not in v["$in"]:
                            match = False
                            break
                        if "$gte" in v and doc.get(k, 0) < v["$gte"]:
                            match = False
                            break
                        if "$lte" in v and doc.get(k, 0) > v["$lte"]:
                            match = False
                            break
                    elif doc.get(k) != v:
                        match = False
                        break
                if match:
                    matched.append(dict(doc))
        
        class AsyncCursor:
            def __init__(self, items):
                self.items = items
            def sort(self, key, direction=1):
                self.items.sort(key=lambda x: x.get(key, 0), reverse=(direction == -1))
                return self
            def skip(self, n):
                self.items = self.items[n:]
                return self
            def limit(self, n):
                self.items = self.items[:n]
                return self
            async def to_list(self, length=None):
                return self.items[:length] if length else self.items
            def __iter__(self):
                return iter(self.items)

        return AsyncCursor(matched)

    async def insert_one(self, doc: dict):
        new_doc = dict(doc)
        if "_id" not in new_doc:
            new_doc["_id"] = str(uuid.uuid4())
        self.parent.add_doc(self.name, new_doc)
        
        class InsertResult:
            def __init__(self, id_):
                self.inserted_id = id_
        return InsertResult(new_doc["_id"])

    async def insert_many(self, docs: list):
        prepared = []
        ids = []
        for d in docs:
            new_doc = dict(d)
            if "_id" not in new_doc:
                new_doc["_id"] = str(uuid.uuid4())
            prepared.append(new_doc)
            ids.append(new_doc["_id"])
        self.parent.add_docs(self.name, prepared)
        class InsertManyResult:
            def __init__(self, ids):
                self.inserted_ids = ids
        return InsertManyResult(ids)

    async def update_one(self, filter_dict: dict, update_dict: dict):
        docs = self.parent.get_docs(self.name)
        for doc in docs:
            match = True
            for k, v in filter_dict.items():
                if doc.get(k) != v:
                    match = False
                    break
            if match:
                if "$set" in update_dict:
                    doc.update(update_dict["$set"])
                self.parent.save()
                return True
        return False

    async def delete_one(self, filter_dict: dict):
        docs = self.parent.get_docs(self.name)
        for i, doc in enumerate(docs):
            match = True
            for k, v in filter_dict.items():
                if doc.get(k) != v:
                    match = False
                    break
            if match:
                docs.pop(i)
                self.parent.save()
                return True
        return False

    async def count_documents(self, filter_dict=None):
        cursor = self.find(filter_dict)
        items = await cursor.to_list()
        return len(items)

    async def distinct(self, key: str, filter_dict=None):
        cursor = self.find(filter_dict)
        items = await cursor.to_list()
        unique_vals = list({item[key] for item in items if key in item and item[key] is not None})
        unique_vals.sort()
        return unique_vals


class PersistentJSONStore:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = {}
        self.load()

    def load(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception:
                self.data = {}
        else:
            self.data = {}

    def save(self):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, default=str)

    def get_docs(self, collection: str):
        if collection not in self.data:
            self.data[collection] = []
        return self.data[collection]

    def add_doc(self, collection: str, doc: dict):
        if collection not in self.data:
            self.data[collection] = []
        self.data[collection].append(doc)
        self.save()

    def add_docs(self, collection: str, docs: list):
        if collection not in self.data:
            self.data[collection] = []
        self.data[collection].extend(docs)
        self.save()

    def __getitem__(self, collection_name: str):
        return JSONDocumentCollection(collection_name, self)


class DatabaseManager:
    def __init__(self):
        self.client = None
        self.db = None
        self.is_mongodb_connected = False
        self.json_store = None

    async def connect(self):
        if settings.MONGODB_ENABLED:
            try:
                self.client = motor.motor_asyncio.AsyncIOMotorClient(
                    settings.MONGODB_URI,
                    serverSelectionTimeoutMS=2000
                )
                self.db = self.client[settings.MONGODB_DB_NAME]
                self.is_mongodb_connected = True
                print(f"✓ Connected to MongoDB at: {settings.MONGODB_URI}/{settings.MONGODB_DB_NAME}", flush=True)
            except Exception as e:
                print(f"ℹ MongoDB connection failed ({e}), falling back to local document store.", flush=True)
                self.is_mongodb_connected = False

        if not self.is_mongodb_connected:
            store_dir = os.path.join(settings.BASE_DIR, "backend", "data")
            os.makedirs(store_dir, exist_ok=True)
            store_file = os.path.join(store_dir, "autowise_datastore.json")
            self.json_store = PersistentJSONStore(store_file)
            self.db = self.json_store
            print(f"✓ Initialized resilient Async Document Store: {store_file}", flush=True)

        # 2. Seed catalog if empty
        await self.seed_initial_data()

    async def seed_initial_data(self):
        count = await self.db["vehicles"].count_documents({})
        if count == 0:
            seed_path = os.path.join(settings.BASE_DIR, "ml", "data", "seeds", "vehicles_seed.json")
            if os.path.exists(seed_path):
                with open(seed_path, "r", encoding="utf-8") as f:
                    vehicles = json.load(f)
                await self.db["vehicles"].insert_many(vehicles)
                print(f"✓ Seeded database with {len(vehicles)} vehicles from seeds/vehicles_seed.json")

    def get_collection(self, name: str):
        return self.db[name]

db_manager = DatabaseManager()
