"""Configuration for the PEP MCP server."""

from __future__ import annotations

import os
from dataclasses import dataclass
from enum import StrEnum


class Environment(StrEnum):
    PROD = "prod"
    DEV = "dev"


# Base URLs per environment
_BASE_URLS = {
    Environment.PROD: {
        "api": "https://delta-api.primer.ai",
        "sso": "https://sso.primer.ai/api",
    },
    Environment.DEV: {
        "api": "https://delta-api.dev.primering.net",
        "sso": "https://sso.dev.primering.net/api",
    },
}


@dataclass(frozen=True)
class PEPConfig:
    """PEP server configuration, resolved from environment variables."""

    env: Environment
    api_base_url: str
    sso_base_url: str
    username: str
    password: str

    @classmethod
    def from_env(cls) -> PEPConfig:
        env = Environment(os.environ.get("PEP_ENV", "prod"))
        urls = _BASE_URLS[env]
        return cls(
            env=env,
            api_base_url=os.environ.get("PEP_API_URL", urls["api"]),
            sso_base_url=os.environ.get("PEP_SSO_URL", urls["sso"]),
            username=os.environ.get("PEP_USERNAME", ""),
            password=os.environ.get("PEP_PASSWORD", ""),
        )


# Singleton — initialized once on import
config = PEPConfig.from_env()
