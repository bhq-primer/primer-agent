"""Resources: AI briefings list and details."""

from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP

from primer_agent.client import pep_client


def register(mcp: FastMCP) -> None:
    @mcp.resource("pep://briefings")
    async def list_briefings() -> str:
        """List user's AI briefings with schedule and status."""
        data = await pep_client.list_scheduled_searches(page_size=50)
        return json.dumps(data, indent=2)

    @mcp.resource("pep://briefings/{briefing_id}")
    async def get_briefing(briefing_id: str) -> str:
        """AI briefing details including latest computed results."""
        briefing = await pep_client.get_scheduled_search(briefing_id)
        results = await pep_client.get_scheduled_search_results(briefing_id, page_size=5)
        return json.dumps(
            {"briefing": briefing, "latest_results": results},
            indent=2,
        )
