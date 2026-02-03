"""LanceDB-backed memory storage with vector search."""

import lancedb
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
import os
import pyarrow as pa

logger = logging.getLogger(__name__)


class MemoryStore:
    """Vector memory store using LanceDB."""
    
    def __init__(self, db_path: str = "/data/memory.lance"):
        self.db_path = db_path
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Connect to LanceDB
        self.db = lancedb.connect(db_path)
        
        # Initialize table
        self._init_table()
        
        logger.info(f"Initialized MemoryStore at {db_path}")
    
    def _init_table(self):
        """Initialize or open the memories table."""
        try:
            self.table = self.db.open_table("memories")
            logger.info(f"Opened existing table (count: {len(self.table)})")
        except Exception:
            # Table doesn't exist yet - will be created on first store
            logger.info("Table doesn't exist yet - will be created on first store")
            self.table = None
    
    def _create_schema(self):
        """Create PyArrow schema for the memories table."""
        return pa.schema([
            pa.field("id", pa.string()),
            pa.field("content", pa.string()),
            pa.field("embedding", pa.list_(pa.float32(), 768)),  # Fixed size float32 vector
            pa.field("tier", pa.string()),
            pa.field("user_id", pa.string()),
            pa.field("importance", pa.int64()),
            pa.field("timestamp", pa.string()),
            pa.field("metadata", pa.string())
        ])
    
    def store(
        self,
        content: str,
        embedding: List[float],
        tier: str = "user",
        user_id: str = "default",
        importance: int = 5,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store a memory with its embedding.
        
        Args:
            content: Text content of the memory
            embedding: Vector embedding
            tier: Memory tier (global, user, session)
            user_id: User identifier
            importance: Importance score (0-10)
            metadata: Optional metadata dict
            
        Returns:
            Memory ID
        """
        import json
        
        memory_id = f"mem_{int(datetime.now().timestamp() * 1000)}"
        timestamp = datetime.now().isoformat()
        
        # Convert embedding to float32 list
        embedding_float32 = [float(x) for x in embedding]
        
        record = {
            "id": memory_id,
            "content": content,
            "embedding": embedding_float32,
            "tier": tier,
            "user_id": user_id,
            "importance": importance,
            "timestamp": timestamp,
            "metadata": json.dumps(metadata or {})
        }
        
        # Create table on first store if it doesn't exist
        if self.table is None:
            schema = self._create_schema()
            data = pa.Table.from_pylist([record], schema=schema)
            self.table = self.db.create_table("memories", data=data)
            logger.info("Created new memories table with PyArrow schema")
        else:
            self.table.add([record])
        
        logger.info(
            f"Stored memory {memory_id} [tier={tier}, user={user_id}, importance={importance}]"
        )
        
        return memory_id
    
    def search(
        self,
        query_embedding: List[float],
        tier: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 5,
        min_importance: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Semantic search for memories using vector similarity.
        
        Args:
            query_embedding: Query vector
            tier: Optional tier filter
            user_id: Optional user filter
            limit: Max results to return
            min_importance: Minimum importance score
            
        Returns:
            List of matching memories with similarity scores
        """
        import json
        
        # Return empty if no table yet
        if self.table is None:
            logger.info("No memories stored yet")
            return []
        
        # Convert query embedding to float32 list
        query_float32 = [float(x) for x in query_embedding]
        
        # Build filter query
        filters = []
        if tier:
            filters.append(f"tier = '{tier}'")
        if user_id:
            filters.append(f"user_id = '{user_id}'")
        if min_importance > 0:
            filters.append(f"importance >= {min_importance}")
        
        # Perform vector search
        query = self.table.search(query_float32, vector_column_name="embedding").limit(limit)
        
        if filters:
            query = query.where(" AND ".join(filters))
        
        results = query.to_list()
        
        # Parse metadata and add similarity scores
        parsed_results = []
        for r in results:
            parsed_results.append({
                "id": r.get("id"),
                "content": r.get("content"),
                "tier": r.get("tier"),
                "user_id": r.get("user_id"),
                "importance": r.get("importance"),
                "timestamp": r.get("timestamp"),
                "metadata": json.loads(r.get("metadata", "{}")),
                "similarity": r.get("_distance", 0.0)  # LanceDB adds distance
            })
        
        logger.info(
            f"Search returned {len(parsed_results)} results "
            f"[tier={tier}, user={user_id}, limit={limit}]"
        )
        
        return parsed_results
    
    def get_by_id(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific memory by ID."""
        import json
        
        results = self.table.search().where(f"id = '{memory_id}'").limit(1).to_list()
        
        if not results:
            return None
        
        r = results[0]
        return {
            "id": r.get("id"),
            "content": r.get("content"),
            "tier": r.get("tier"),
            "user_id": r.get("user_id"),
            "importance": r.get("importance"),
            "timestamp": r.get("timestamp"),
            "metadata": json.loads(r.get("metadata", "{}"))
        }
    
    def count(self, tier: Optional[str] = None, user_id: Optional[str] = None) -> int:
        """Count memories with optional filters."""
        if self.table is None:
            return 0
            
        filters = []
        if tier:
            filters.append(f"tier = '{tier}'")
        if user_id:
            filters.append(f"user_id = '{user_id}'")
        
        if filters:
            return len(self.table.search().where(" AND ".join(filters)).limit(100000).to_list())
        else:
            return len(self.table)
    
    def delete_old(self, tier: str, retention_days: int):
        """Delete memories older than retention period for a given tier."""
        from datetime import timedelta
        
        if retention_days < 0:
            return  # Forever retention
        
        cutoff = datetime.now() - timedelta(days=retention_days)
        cutoff_iso = cutoff.isoformat()
        
        # LanceDB delete by filter
        self.table.delete(f"tier = '{tier}' AND timestamp < '{cutoff_iso}'")
        
        logger.info(f"Deleted old memories for tier={tier} (retention={retention_days}d)")
