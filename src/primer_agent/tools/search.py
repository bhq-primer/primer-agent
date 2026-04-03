"""Tool: search — Search documents in PEP."""

from __future__ import annotations

from mcp.server.fastmcp import Context, FastMCP

from primer_agent.client import pep_client


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def search(
        query: str,
        mode: str = "concept",
        start_date: str | None = None,
        end_date: str | None = None,
        sources: list[str] | None = None,
        page_size: int = 20,
        ctx: Context | None = None,
    ) -> dict:
        """Search documents in PEP.

        Performs a standalone search across all available documents.

        Args:
            query: Search query text.
            mode: Search mode — "concept" (semantic) or "terms" (boolean).
            start_date: Filter documents published after this date (ISO format).
            end_date: Filter documents published before this date (ISO format).
            sources: Filter by data source names (e.g. ["news", "social"]).
            page_size: Number of results to return (default 20, max 1000).
        """
        if ctx:
            await ctx.report_progress(0, 1, "Searching...")

        results = await pep_client.search_documents(
            query,
            mode=mode,
            start_date=start_date,
            end_date=end_date,
            sources=sources,
            page_size=page_size,
        )

        if ctx:
            count = len(results.get("results", []))
            await ctx.report_progress(1, 1, f"Found {count} documents")

        return results
