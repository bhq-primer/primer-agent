"""Discovery prompts — help users explore what they already have in PEP."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP


def register(mcp: FastMCP) -> None:
    @mcp.prompt()
    def my_workspaces() -> str:
        """List my workspaces with key stats."""
        return (
            "Read the pep://workspaces resource and present a summary of my workspaces. "
            "For each workspace, show: name, document count (if available from insights), "
            "investigation state, and when it was last updated. "
            "Format as a table. If there are no workspaces, suggest creating one."
        )

    @mcp.prompt()
    def my_briefings() -> str:
        """List my AI briefings with schedule and status."""
        return (
            "Read the pep://briefings resource and present a summary of my AI briefings. "
            "For each briefing, show: name, search query, schedule (frequency and time), "
            "whether it's enabled, and when it last ran. "
            "Format as a table. If there are no briefings, suggest creating one."
        )

    @mcp.prompt()
    def workspace_summary(workspace_id: str) -> str:
        """Summarize a workspace: documents, narratives, topics, recent chat."""
        return (
            f"Read these resources and present a comprehensive summary:\n"
            f"1. pep://workspaces/{workspace_id} — workspace metadata\n"
            f"2. pep://workspaces/{workspace_id}/documents — document list\n"
            f"3. pep://workspaces/{workspace_id}/narratives — narratives (if computed)\n"
            f"4. pep://workspaces/{workspace_id}/topics — topics (if computed)\n\n"
            f"Present:\n"
            f"- Workspace name and state\n"
            f"- Total document count and top sources\n"
            f"- Key narratives (if available)\n"
            f"- Key topics (if available)\n"
            f"- Suggest next steps (e.g. chat to explore, check timeline)"
        )

    @mcp.prompt()
    def briefing_latest(briefing_id: str) -> str:
        """Show the latest results from a specific AI briefing."""
        return (
            f"Read the pep://briefings/{briefing_id} resource and present the latest results. "
            f"Show the briefing name, when it last ran, and summarize the computed insights "
            f"(themes, summaries, etc.). Highlight the most important findings."
        )
