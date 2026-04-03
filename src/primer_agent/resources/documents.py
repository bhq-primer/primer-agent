"""Resource: pep://documents/{id} — single document with full text."""

from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP

from primer_agent.client import pep_client


def register(mcp: FastMCP) -> None:
    @mcp.resource("pep://documents/{document_id}")
    async def get_document(document_id: str) -> str:
        """Single document with full text and metadata."""
        data = await pep_client.get_document(document_id)
        return json.dumps(data, indent=2)
