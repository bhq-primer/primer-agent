"""Tool: create_briefing — Create a recurring AI briefing in PEP."""

from __future__ import annotations

from mcp.server.fastmcp import Context, FastMCP

from primer_agent.client import pep_client


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def create_briefing(
        name: str,
        query: str,
        mode: str = "concept",
        schedule_time: str = "09:00",
        schedule_frequency: str = "daily",
        asset_types: list[str] | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        sources: list[str] | None = None,
        ctx: Context | None = None,
    ) -> dict:
        """Create a recurring AI briefing in PEP.

        Sets up a scheduled search that runs on a cadence and automatically
        computes insights (e.g. narratives, topics, summaries).

        Args:
            name: Briefing name.
            query: Search query for the briefing.
            mode: Search mode — "concept" (semantic) or "terms" (boolean).
            schedule_time: Time to run (HH:MM in UTC, default "09:00").
            schedule_frequency: Frequency — "daily", "hourly", or "weekly".
            asset_types: Insight types to compute (e.g. ["theme-sets", "rag-v-summary"]).
                Defaults to ["theme-sets"] if not provided.
            start_date: Initial date range start (ISO format).
            end_date: Initial date range end (ISO format).
            sources: Filter by data source names.
        """
        if ctx:
            await ctx.report_progress(0, 2, "Creating AI briefing...")

        if asset_types is None:
            asset_types = ["theme-sets"]

        # Build search request
        search_query = (
            {"concept": query, "mode": "concept"} if mode == "concept"
            else {"terms": query, "mode": "terms"}
        )
        search_request: dict = {"search": {"query": search_query}, "results": {"page_size": 1000}}

        if start_date or end_date:
            search_request["search"]["published"] = {}
            if start_date:
                search_request["search"]["published"]["start_date"] = start_date
            if end_date:
                search_request["search"]["published"]["end_date"] = end_date
        if sources:
            search_request["search"].setdefault("metadata", {})["items"] = [
                {"key": "data_source_name", "value": s} for s in sources
            ]

        # Parse schedule time
        hour, minute = (int(x) for x in schedule_time.split(":"))
        schedule: dict
        if schedule_frequency == "daily":
            schedule = {"type": "daily", "time_to_run": {"hour": hour, "minute": minute}}
        elif schedule_frequency == "hourly":
            schedule = {"type": "hourly", "minute": minute}
        elif schedule_frequency == "weekly":
            schedule = {
                "type": "weekly",
                "day": "monday",
                "time_to_run": {"hour": hour, "minute": minute},
            }
        else:
            schedule = {"type": "daily", "time_to_run": {"hour": hour, "minute": minute}}

        body = {
            "name": name,
            "search_request": search_request,
            "schedule": schedule,
            "scheduled_assets": [{"asset_type": at} for at in asset_types],
        }

        if ctx:
            await ctx.report_progress(1, 2, "Submitting to PEP...")

        result = await pep_client.create_scheduled_search(body)

        if ctx:
            await ctx.report_progress(2, 2, "AI briefing created")

        return {
            "briefing_id": result.get("id"),
            "name": name,
            "schedule": schedule_frequency,
            "asset_types": asset_types,
            "message": f"AI briefing '{name}' created — runs {schedule_frequency} at {schedule_time} UTC.",
        }
