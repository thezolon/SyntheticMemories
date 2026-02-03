"""
Pydantic models for Memory Agent
"""

from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class Memory(BaseModel):
    """A stored memory"""

    id: str = Field(default_factory=lambda: f"mem_{uuid4().hex[:8]}")
    content: str
    embedding: Optional[List[float]] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    tags: List[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

    def model_dump(self, **kwargs):
        """Override to ensure datetime is serialized properly"""
        data = super().model_dump(**kwargs)
        if isinstance(data.get("timestamp"), datetime):
            data["timestamp"] = data["timestamp"].isoformat()
        return data


class SearchResult(BaseModel):
    """Search result with similarity score"""

    memory: Memory
    score: float


class QueryResult(BaseModel):
    """Result from LLM query"""

    answer: str
    sources: List[str]
    confidence: Optional[float] = None
