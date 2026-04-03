"""Tool: create_workspace — Create a new PEP workspace, optionally seeded with search results."""

from __future__ import annotations

from mcp.server.fastmcp import Context, FastMCP

from primer_agent.client import pep_client


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def create_workspace(
        name: str,
        query: str | None = None,
        mode: str = "concept",
        start_date: str | None = None,
        end_date: str | None = None,
        sources: list[str] | None = None,
        max_documents: int = 100,
        ctx: Context | None = None,
    ) -> dict:
        """Create a new PEP workspace.

        If a query is provided, searches for documents and adds them to the
        workspace's dataverse automatically.

        Args:
            name: Human-readable workspace name.
            query: Optional search query to seed the workspace with documents.
            mode: Search mode — "concept" (semantic) or "terms" (boolean).
            start_date: Filter documents published after this date (ISO format).
            end_date: Filter documents published before this date (ISO format).
            sources: Filter by data source names (e.g. ["news", "social"]).
            max_documents: Maximum documents to add (default 100).
        """
        # Step 1: Create workspace
        if ctx:
            await ctx.report_progress(0, 4 if query else 1, "Creating workspace...")

        workspace = await pep_client.create_workspace(name)
        workspace_id = workspace["id"]
        dataverse_id = workspace["dataverse_id"]
        conversation_id = workspace.get("conversation_ids", [None])[0]

        if not query:
            if ctx:
                await ctx.report_progress(1, 1, "Workspace created")
            return {
                "workspace_id": workspace_id,
                "dataverse_id": dataverse_id,
                "conversation_id": conversation_id,
                "message": f"Workspace '{name}' created (empty).",
            }

        # Step 2: Search for documents
        if ctx:
            await ctx.report_progress(1, 4, "Searching for documents...")

        search_body = {
            "search": {
                "query": {"concept": query, "mode": mode} if mode == "concept"
                else {"terms": query, "mode": "terms"},
            },
            "results": {"page": 1, "page_size": max_documents},
        }
        if start_date or end_date:
            search_body["search"]["published"] = {}
            if start_date:
                search_body["search"]["published"]["start_date"] = start_date
            if end_date:
                search_body["search"]["published"]["end_date"] = end_date
        if sources:
            search_body["search"].setdefault("metadata", {})["items"] = [
                {"key": "data_source_name", "value": s} for s in sources
            ]

        # Step 3: Add search results to dataverse
        if ctx:
            await ctx.report_progress(2, 4, "Adding documents to workspace...")

        result = await pep_client.add_search_to_dataverse(dataverse_id, search_body)
        doc_count = (
            result.get("action", {}).get("unique_documents_added")
            or len(result.get("version", {}).get("document_ids", []))
        )

        # Step 4: Done
        if ctx:
            await ctx.report_progress(4, 4, f"Workspace ready with {doc_count} documents")

        return {
            "workspace_id": workspace_id,
            "dataverse_id": dataverse_id,
            "conversation_id": conversation_id,
            "document_count": doc_count,
            "message": f"Workspace '{name}' created with {doc_count} documents.",
        }
