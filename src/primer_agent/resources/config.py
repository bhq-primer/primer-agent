"""Resource: pep://config — environment and auth status."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from primer_agent.auth import token_manager
from primer_agent.config import config


def register(mcp: FastMCP) -> None:
    @mcp.resource("pep://config")
    async def get_config() -> dict:
        """Current PEP environment configuration and auth status."""
        has_token = token_manager._token is not None
        return {
            "environment": config.env.value,
            "api_base_url": config.api_base_url,
            "authenticated": has_token,
            "username": config.username or "(not set)",
        }
