
import httpx
import pytest

from oauth_by_hand.token_exchange import exchange_google_code


@pytest.mark.asyncio
async def test_successful_token_exchange(monkeypatch):
    async def fake_post(self, url, **kwargs):
        assert url == "https://oauth2.googleapis.com/token"
        assert kwargs["data"]["code_verifier"] == "test-verifier"
        assert kwargs["data"]["grant_type"] == "authorization_code"

        return httpx.Response(
            200,
            json={
                "access_token": "fake-access-token",
                "token_type": "Bearer",
                "expires_in": 3600,
                "id_token": "fake-id-token",
            },
            request=httpx.Request("POST", url),
        )

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)

    result = await exchange_google_code(
        code="test-code",
        code_verifier="test-verifier",
        client_id="test-client",
        client_secret="test-secret",
        redirect_uri="http://127.0.0.1:8000/auth/google/callback",
    )

    assert result["access_token"] == "fake-access-token"


@pytest.mark.asyncio
async def test_invalid_authorization_code(monkeypatch):
    async def fake_post(self, url, **kwargs):
        return httpx.Response(
            400,
            json={"error": "invalid_grant"},
            request=httpx.Request("POST", url),
        )

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)

    with pytest.raises(httpx.HTTPStatusError):
        await exchange_google_code(
            code="invalid-code",
            code_verifier="test-verifier",
            client_id="test-client",
            client_secret="test-secret",
            redirect_uri="http://127.0.0.1:8000/auth/google/callback",
        )


@pytest.mark.asyncio
async def test_missing_parameters():
    with pytest.raises(ValueError):
        await exchange_google_code(
            code="",
            code_verifier="",
            client_id="test-client",
            client_secret="",
            redirect_uri="http://127.0.0.1:8000/callback",
        )
