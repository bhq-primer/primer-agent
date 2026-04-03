"""Resources: workspaces, workspace details, and workspace tab content."""

from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP

from primer_agent.client import pep_client


def register(mcp: FastMCP) -> None:
    # -------------------------------------------------------------------------
    # Workspace list
    # -------------------------------------------------------------------------

    @mcp.resource("pep://workspaces")
    async def list_workspaces() -> str:
        """List user's workspaces with key metadata."""
        data = await pep_client.list_workspaces(page_size=50)
        workspaces = data.get("workspaces", [])
        return json.dumps(
            [
                {
                    "id": w["id"],
                    "name": w["name"],
                    "dataverse_id": w["dataverse_id"],
                    "investigation_state": w.get("investigation_state"),
                    "insights": w.get("insights"),
                    "created_at": w.get("created_at"),
                    "updated_at": w.get("updated_at"),
                }
                for w in workspaces
            ],
            indent=2,
        )

    # -------------------------------------------------------------------------
    # Single workspace
    # -------------------------------------------------------------------------

    @mcp.resource("pep://workspaces/{workspace_id}")
    async def get_workspace(workspace_id: str) -> str:
        """Workspace details including conversation IDs and state."""
        data = await pep_client.get_workspace(workspace_id)
        return json.dumps(data, indent=2)

    # -------------------------------------------------------------------------
    # Workspace documents
    # -------------------------------------------------------------------------

    @mcp.resource("pep://workspaces/{workspace_id}/documents")
    async def get_workspace_documents(workspace_id: str) -> str:
        """Documents in a workspace's dataverse."""
        workspace = await pep_client.get_workspace(workspace_id)
        dataverse_id = workspace["dataverse_id"]
        data = await pep_client.list_dataverse_documents(dataverse_id, page_size=50)
        return json.dumps(data, indent=2)

    # -------------------------------------------------------------------------
    # Workspace insight tabs
    # -------------------------------------------------------------------------

    @mcp.resource("pep://workspaces/{workspace_id}/narratives")
    async def get_workspace_narratives(workspace_id: str) -> str:
        """Narratives computed for this workspace."""
        return await _get_workspace_asset(workspace_id, "theme-sets")

    @mcp.resource("pep://workspaces/{workspace_id}/topics")
    async def get_workspace_topics(workspace_id: str) -> str:
        """Topics computed for this workspace."""
        return await _get_workspace_asset(workspace_id, "topic-summaries")

    @mcp.resource("pep://workspaces/{workspace_id}/timeline")
    async def get_workspace_timeline(workspace_id: str) -> str:
        """Timeline computed for this workspace."""
        return await _get_workspace_asset(workspace_id, "timeline")

    @mcp.resource("pep://workspaces/{workspace_id}/quotes")
    async def get_workspace_quotes(workspace_id: str) -> str:
        """Quotes extracted for this workspace."""
        return await _get_workspace_asset(workspace_id, "quotes")


async def _get_workspace_asset(workspace_id: str, asset_type: str) -> str:
    """Fetch the latest asset of a given type for a workspace's dataverse."""
    workspace = await pep_client.get_workspace(workspace_id)
    dataverse_id = workspace["dataverse_id"]

    assets = await pep_client.list_assets(dataverse_id, asset_type, page_size=1)
    items = assets.get("items", assets.get("results", []))
    if not items:
        return json.dumps({"status": "not_computed", "asset_type": asset_type})

    latest = items[0]
    asset_id = latest.get("asset_id", latest.get("id"))
    status = latest.get("status", "unknown")

    if status == "complete":
        results = await pep_client.get_asset_results(asset_type, asset_id)
        return json.dumps(results, indent=2)

    return json.dumps(
        {"status": status, "asset_type": asset_type, "asset_id": asset_id},
        indent=2,
    )
