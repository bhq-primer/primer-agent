"""PEP authentication — SSO login and token management."""

from __future__ import annotations

import time

import httpx

from primer_agent.config import config


class AuthError(Exception):
    pass


class TokenManager:
    """Manages PEP API tokens with lazy login and refresh."""

    def __init__(self) -> None:
        self._token: str | None = None
        self._expires_at: float = 0

    async def get_token(self) -> str:
        if self._token and time.time() < self._expires_at:
            return self._token
        await self._login()
        if not self._token:
            raise AuthError("Failed to obtain PEP API token")
        return self._token

    async def _login(self) -> None:
        if not config.username or not config.password:
            raise AuthError(
                "PEP_USERNAME and PEP_PASSWORD must be set. "
                "See README for configuration instructions."
            )
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{config.sso_base_url}/v1/auth/login",
                json={"username": config.username, "password": config.password},
            )
            if resp.status_code != 200:
                raise AuthError(f"Login failed: {resp.status_code} {resp.text}")
            data = resp.json()
            self._token = data["access_token"]
            # Refresh 5 minutes before expiry; default to 55 min if not provided
            expires_in = data.get("expires_in", 3300)
            self._expires_at = time.time() + expires_in - 300

    def auth_headers(self, token: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {token}"}


# Singleton
token_manager = TokenManager()
