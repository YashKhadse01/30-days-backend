
from fastapi import FastAPI, Request
from prometheus_fastapi_instrumentator import Instrumentator
from strawberry.fastapi import GraphQLRouter

from graphql_performance_api.schema import schema
from graphql_performance_api.dataloaders import (
    create_project_loader,
)


async def get_context(request: Request) -> dict:
    """Create a fresh GraphQL context for each request."""
    return {
        "request": request,
        "project_loader": create_project_loader(),
    }


app = FastAPI(
    title="Day 26 - GraphQL Performance API",
    description="Strawberry GraphQL with FastAPI and Prometheus monitoring",
    version="0.1.0",
)

# Register GraphQL endpoint.
graphql_router = GraphQLRouter(
    schema,
    context_getter=get_context,
)

app.include_router(graphql_router, prefix="/graphql")


@app.get("/health", tags=["Monitoring"])
async def health():
    """Basic application health check."""
    return {"status": "healthy"}


# Instrument FastAPI to collect HTTP metrics.
Instrumentator(
    should_group_status_codes=False,
    should_ignore_untemplated=True,
    should_instrument_requests_inprogress=True,
    excluded_handlers=["/metrics"],
).instrument(app).expose(
    app,
    endpoint="/metrics",
    include_in_schema=False,
)
