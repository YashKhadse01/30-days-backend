
import hmac

from fastapi import Request
from pydantic_settings import BaseSettings, SettingsConfigDict
from strawberry.exceptions import GraphQLError


class Settings(BaseSettings):
    graphql_api_key: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()


def require_api_key(info) -> None:
    """Authorize protected GraphQL operations."""

    request: Request = info.context["request"]

    provided_key = request.headers.get("X-API-Key", "")

    if not provided_key or not hmac.compare_digest(
        provided_key,
        settings.graphql_api_key,
    ):
        raise GraphQLError("Unauthorized")
