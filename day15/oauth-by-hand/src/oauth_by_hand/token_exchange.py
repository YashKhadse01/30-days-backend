
import httpx


GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"


async def exchange_google_code(
    code: str,
    code_verifier: str,
    client_id: str,
    client_secret: str,
    redirect_uri: str,
) -> dict:
    """Exchange an authorization code for Google tokens."""

    if not all([
        code,
        code_verifier,
        client_id,
        redirect_uri,
    ]):
        raise ValueError("Missing required OAuth parameters")

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "code_verifier": code_verifier,
    }

    if client_secret:
        data["client_secret"] = client_secret

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            GOOGLE_TOKEN_URL,
            data=data,
            headers={
                "Accept": "application/json",
            },
        )

        response.raise_for_status()
        tokens = response.json()

    if not isinstance(tokens, dict):
        raise ValueError("Invalid OAuth token response")

    if not isinstance(tokens.get("access_token"), str):
        raise ValueError("Missing OAuth access token")

    if not tokens["access_token"]:
        raise ValueError("Empty OAuth access token")

    return tokens
