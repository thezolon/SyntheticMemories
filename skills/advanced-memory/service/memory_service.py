"""Advanced Memory Service - FastAPI server."""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import yaml
import logging
import os
from datetime import datetime

from embeddings import EmbeddingClient
from importance_scorer import ImportanceScorer
from memory_store import MemoryStore

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load config
config_path = os.getenv("CONFIG_PATH", "/app/config.yml")
with open(config_path) as f:
    config = yaml.safe_load(f)

# Initialize components
embeddings = EmbeddingClient(
    host=config['ollama']['host'],
    model=config['ollama']['model']
)
scorer = ImportanceScorer()
store = MemoryStore(db_path=config['lancedb']['path'])

# FastAPI app
app = FastAPI(title="Advanced Memory Service", version="0.1.0")

# Serve web UI
app.mount("/ui", StaticFiles(directory="/app/web", html=True), name="ui")


# Request/Response models
class StoreRequest(BaseModel):
    content: str = Field(..., description="Memory content")
    tier: str = Field("user", description="Memory tier (global, user, session)")
    user_id: str = Field("default", description="User identifier")
    importance: Optional[int] = Field(None, description="Manual importance (0-10)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")


class StoreResponse(BaseModel):
    success: bool
    memory_id: str
    importance: int
    tier: str


class RecallResponse(BaseModel):
    results: List[Dict[str, Any]]
    query: str
    count: int


class CurateRequest(BaseModel):
    source_file: str = Field(..., description="Path to source markdown file")
    threshold: int = Field(7, description="Minimum importance for curation")
    dry_run: bool = Field(False, description="Preview without writing")


class CurateResponse(BaseModel):
    extracted: int
    appended_to_memory: bool
    items: List[Dict[str, Any]]


class HealthResponse(BaseModel):
    status: str
    ollama_connected: bool
    embedding_model: str
    db_path: str
    memory_count: int


# Endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Service health check."""
    ollama_ok = embeddings.health_check()
    
    return HealthResponse(
        status="healthy" if ollama_ok else "degraded",
        ollama_connected=ollama_ok,
        embedding_model=config['ollama']['model'],
        db_path=config['lancedb']['path'],
        memory_count=store.count()
    )


@app.post("/store", response_model=StoreResponse)
async def store_memory(request: StoreRequest):
    """Store a new memory with automatic embedding and importance scoring."""
    try:
        # Score importance if not provided
        if request.importance is None:
            importance = scorer.score(request.content, request.metadata)
        else:
            importance = max(0, min(10, request.importance))
        
        # Check if meets storage threshold
        threshold = config['memory']['importance_threshold']
        if importance < threshold:
            logger.info(f"Skipping low-importance memory (score={importance} < {threshold})")
            raise HTTPException(
                status_code=400,
                detail=f"Memory importance ({importance}) below threshold ({threshold})"
            )
        
        # Generate embedding
        embedding = embeddings.embed(request.content)
        
        # Store
        memory_id = store.store(
            content=request.content,
            embedding=embedding,
            tier=request.tier,
            user_id=request.user_id,
            importance=importance,
            metadata=request.metadata
        )
        
        logger.info(f"Stored memory {memory_id} [importance={importance}, tier={request.tier}]")
        
        return StoreResponse(
            success=True,
            memory_id=memory_id,
            importance=importance,
            tier=request.tier
        )
    
    except HTTPException:
        # Re-raise HTTPExceptions as-is (don't convert to 500)
        raise
    except Exception as e:
        logger.error(f"Store failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/recall", response_model=RecallResponse)
async def recall_memories(
    query: str,
    tier: Optional[str] = None,
    user_id: Optional[str] = None,
    limit: int = 5,
    min_importance: int = 0
):
    """Semantic search for memories."""
    try:
        # Generate query embedding
        query_embedding = embeddings.embed(query)
        
        # Search
        results = store.search(
            query_embedding=query_embedding,
            tier=tier,
            user_id=user_id,
            limit=limit,
            min_importance=min_importance
        )
        
        logger.info(f"Recall query '{query}' returned {len(results)} results")
        
        return RecallResponse(
            results=results,
            query=query,
            count=len(results)
        )
    
    except Exception as e:
        logger.error(f"Recall failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/curate", response_model=CurateResponse)
async def curate_memory_file(request: CurateRequest):
    """Extract high-importance items from a markdown file and store as memories."""
    try:
        # Read source file
        if not os.path.exists(request.source_file):
            raise HTTPException(status_code=404, detail=f"Source file not found: {request.source_file}")
        
        with open(request.source_file, 'r') as f:
            content = f.read()
        
        # Split into meaningful chunks (headers, list items, paragraphs)
        import re
        
        # Extract lines that are likely important:
        # - Headers (##, ###)
        # - List items (-, *, numbers)
        # - Non-empty paragraphs
        chunks = []
        
        for line in content.split('\n'):
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Skip markdown artifacts
            if line.startswith('```') or line.startswith('---'):
                continue
            
            # Keep headers, list items, and substantial text
            if (line.startswith('#') or 
                line.startswith('-') or 
                line.startswith('*') or 
                re.match(r'^\d+\.', line) or
                (len(line) > 20 and not line.startswith('  '))):
                
                # Clean up markdown formatting
                cleaned = re.sub(r'^#+\s*', '', line)  # Remove header markers
                cleaned = re.sub(r'^[-*]\s*', '', cleaned)  # Remove list markers
                cleaned = re.sub(r'^\d+\.\s*', '', cleaned)  # Remove numbered list markers
                cleaned = re.sub(r'\*\*(.*?)\*\*', r'\1', cleaned)  # Remove bold
                cleaned = re.sub(r'\*(.*?)\*', r'\1', cleaned)  # Remove italic
                cleaned = re.sub(r'`(.*?)`', r'\1', cleaned)  # Remove code blocks
                
                if len(cleaned) > 15:  # Only keep substantial content
                    chunks.append(cleaned.strip())
        
        # Score and filter chunks
        high_importance_items = []
        stored_count = 0
        
        for chunk in chunks:
            importance = scorer.score(chunk)
            
            if importance >= request.threshold:
                item = {
                    "content": chunk,
                    "importance": importance
                }
                high_importance_items.append(item)
                
                # Store as memory (unless dry run)
                if not request.dry_run:
                    try:
                        embedding = embeddings.embed(chunk)
                        memory_id = store.store(
                            content=chunk,
                            embedding=embedding,
                            tier="global",  # Curated items are global by default
                            user_id="system",
                            importance=importance,
                            metadata={
                                "source": os.path.basename(request.source_file),
                                "curated_at": datetime.now().isoformat()
                            }
                        )
                        stored_count += 1
                        logger.info(f"Stored curated memory: {memory_id} (importance={importance})")
                    except Exception as e:
                        logger.warning(f"Failed to store chunk: {e}")
        
        # Sort by importance (highest first)
        high_importance_items.sort(key=lambda x: x['importance'], reverse=True)
        
        logger.info(f"Curated {len(high_importance_items)} items from {request.source_file} (stored {stored_count})")
        
        return CurateResponse(
            extracted=len(high_importance_items),
            appended_to_memory=not request.dry_run,
            items=high_importance_items[:20]  # Return top 20 for preview
        )
    
    except Exception as e:
        logger.error(f"Curate failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Root endpoint - redirect to UI."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/ui/index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=config['service']['host'],
        port=config['service']['port'],
        log_level="info"
    )
