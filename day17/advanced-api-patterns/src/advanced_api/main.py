
import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import (
    Depends,
    FastAPI,
    Header,
    HTTPException,
    Request,
    Response,
    status,
)
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from redis.asyncio import Redis

from advanced_api.api_keys import APIKeyManager, APIKeyRecord
from advanced_api.cache import CacheAsideManager
from advanced_api.etags import ETagManager
from advanced_api.idempotency import (
    IdempotencyConflict,
    IdempotencyManager,
)


# =========================================================
# 1. ENVIRONMENT CONFIGURATION
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(
    dotenv_path=PROJECT_ROOT / ".env",
    override=False,
)

REDIS_URL = os.getenv(
    "REDIS_URL",
    "redis://127.0.0.1:6380/0",
)


# =========================================================
# 2. APPLICATION LIFESPAN
# =========================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and close Redis safely."""

    redis_client = Redis.from_url(
        REDIS_URL,
        decode_responses=True,
    )

    app.state.redis = redis_client

    app.state.cache = CacheAsideManager(
        redis=redis_client,
        ttl_seconds=60,
    )

    try:
        await redis_client.ping()
        yield
    finally:
        await redis_client.aclose()


app = FastAPI(
    title="Day 17 - Advanced API Patterns",
    description=(
        "API keys, idempotency, ETags, "
        "and Redis cache-aside patterns."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# =========================================================
# 3. APPLICATION STORAGE AND MANAGERS
# =========================================================

# In-memory demonstration storage.
# Production applications should use persistent storage.

api_key_manager = APIKeyManager()

idempotency_manager = IdempotencyManager(
    ttl_seconds=3600,
)

etag_manager = ETagManager()

items: list[dict] = []


# =========================================================
# 4. PYDANTIC MODELS
# =========================================================

class ItemCreate(BaseModel):
    name: str = Field(min_length=1)
    price: float = Field(gt=0)


# =========================================================
# 5. API KEY AUTHENTICATION
# =========================================================

def require_scope(scope: str):
    """Check API key validity and required scope."""

    def authenticate(
        x_api_key: str | None = Header(default=None),
    ) -> APIKeyRecord:

        if not x_api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key required",
            )

        record = api_key_manager.authenticate(
            x_api_key
        )

        if record is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or revoked API key",
            )

        if scope not in record.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient API key permissions",
            )

        return record

    return authenticate


# =========================================================
# 6. BASIC API ENDPOINTS
# =========================================================

@app.get("/")
def home():
    return {
        "message": "Day 17 Advanced API Patterns",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "advanced-api",
    }


@app.get("/items")
def get_items(
    client: APIKeyRecord = Depends(
        require_scope("read:items")
    ),
):
    return {
        "items": items,
        "client": client.client_name,
    }


# =========================================================
# 7. ITEM CREATION WITH IDEMPOTENCY
# =========================================================

@app.post("/items", status_code=201)
def create_item(
    item: ItemCreate,
    response: Response,
    idempotency_key: str | None = Header(default=None),
    client: APIKeyRecord = Depends(
        require_scope("write:items")
    ),
):
    """Create an item with optional idempotency."""

    def perform_creation() -> dict:

        new_item = {
            "id": len(items) + 1,
            "name": item.name,
            "price": item.price,
        }

        items.append(new_item)

        return {
            "item": new_item,
            "created_by": client.client_name,
        }

    if idempotency_key is None:
        return perform_creation()

    if not idempotency_key.strip():
        raise HTTPException(
            status_code=400,
            detail="Idempotency-Key cannot be empty",
        )

    try:
        result, status_code, replayed = (
            idempotency_manager.execute(
                key=idempotency_key,
                payload=item.model_dump(mode="json"),
                operation=perform_creation,
                status_code=201,
                namespace=(
                    f"items:create:{client.key_id}"
                ),
            )
        )

    except IdempotencyConflict:
        raise HTTPException(
            status_code=409,
            detail=(
                "Idempotency-Key reused with "
                "a different request payload"
            ),
        )

    response.status_code = status_code

    response.headers["Idempotency-Replayed"] = (
        "true" if replayed else "false"
    )

    return result


# =========================================================
# 8. ITEM LOOKUP
# =========================================================

def find_item(item_id: int) -> dict:
    """Find an item in the in-memory storage."""

    for item in items:
        if item["id"] == item_id:
            return item

    raise HTTPException(
        status_code=404,
        detail="Item not found",
    )


def cache_key_for_item(item_id: int) -> str:
    """Namespace cache keys for the Day 17 project."""

    return f"day17:items:{item_id}"


# =========================================================
# 9. GET ITEM WITH REDIS CACHE-ASIDE AND ETAGS
# =========================================================

@app.get("/items/{item_id}")
async def get_item_by_id(
    item_id: int,
    request: Request,
    client: APIKeyRecord = Depends(
        require_scope("read:items")
    ),
):
    cache = request.app.state.cache

    async def load_item():
        # Return a copy so the cached representation
        # is not accidentally mutated in memory.
        return dict(find_item(item_id))

    item, cache_hit = await cache.get_or_load(
        key=cache_key_for_item(item_id),
        loader=load_item,
    )

    etag = etag_manager.generate(item)

    response_headers = {
        "ETag": etag,
        "X-Cache": "HIT" if cache_hit else "MISS",
    }

    if_none_match = request.headers.get(
        "if-none-match"
    )

    if if_none_match is not None:

        validators = [
            value.strip()
            for value in if_none_match.split(",")
        ]

        if (
            "*" in validators
            or etag in validators
            or f"W/{etag}" in validators
        ):
            return Response(
                status_code=304,
                headers=response_headers,
            )

    return JSONResponse(
        content=item,
        headers=response_headers,
    )


# =========================================================
# 10. UPDATE ITEM WITH ETAGS AND CACHE INVALIDATION
# =========================================================

@app.put("/items/{item_id}")
async def update_item_by_id(
    item_id: int,
    updated_item: ItemCreate,
    request: Request,
    client: APIKeyRecord = Depends(
        require_scope("write:items")
    ),
):
    item = find_item(item_id)

    current_etag = etag_manager.generate(item)

    if_match = request.headers.get("if-match")

    if if_match is None:
        raise HTTPException(
            status_code=428,
            detail="If-Match header required",
        )

    validators = [
        value.strip()
        for value in if_match.split(",")
    ]

    # Strong ETag comparison only.
    if not (
        "*" in validators
        or current_etag in validators
    ):
        return JSONResponse(
            status_code=412,
            content={
                "detail": "Resource version mismatch"
            },
            headers={"ETag": current_etag},
        )

    # Update the item.
    item["name"] = updated_item.name
    item["price"] = updated_item.price

    # Invalidate stale cached data.
    await request.app.state.cache.invalidate(
        cache_key_for_item(item_id)
    )

    new_etag = etag_manager.generate(item)

    return JSONResponse(
        content=item,
        headers={
            "ETag": new_etag,
            "X-Cache": "INVALIDATED",
        },
    )
