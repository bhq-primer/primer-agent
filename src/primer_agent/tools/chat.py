"""Tool: chat — Send a message to a workspace conversation agent."""

from __future__ import annotations

import json

from mcp.server.fastmcp import Context, FastMCP

from primer_agent.client import pep_client


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def chat(
        workspace_id: str,
        message: str,
        conversation_id: str | None = None,
        ctx: Context | None = None,
    ) -> dict:
        """Send a message to a PEP workspace conversation agent.

        The agent can search, curate documents, and generate insights within
        the workspace. If conversation_id is not provided, uses the workspace's
        first conversation.

        Args:
            workspace_id: The workspace ID.
            message: The message to send to the agent.
            conversation_id: Optional conversation ID. If omitted, the workspace's
                primary conversation is used.
        """
        # Resolve conversation_id if not provided
        if not conversation_id:
            if ctx:
                await ctx.report_progress(0, 3, "Resolving conversation...")
            workspace = await pep_client.get_workspace(workspace_id)
            conv_ids = workspace.get("conversation_ids", [])
            if not conv_ids:
                return {"error": "No conversations found for this workspace."}
            conversation_id = conv_ids[0]

        # Send message
        if ctx:
            await ctx.report_progress(1, 3, "Sending message to agent...")

        resp = await pep_client.send_message(conversation_id, message)

        # Parse SSE response — collect text content from the stream
        if ctx:
            await ctx.report_progress(2, 3, "Processing agent response...")

        agent_text = _parse_sse_response(resp.text)

        if ctx:
            await ctx.report_progress(3, 3, "Response received")

        return {
            "workspace_id": workspace_id,
            "conversation_id": conversation_id,
            "response": agent_text,
        }


def _parse_sse_response(raw: str) -> str:
    """Extract text content from an SSE response stream.

    Parses AG-UI event stream format. The PEP agent delivers structured
    responses via CUSTOM "chat_with_data" events (containing the main
    analysis) plus TEXT_MESSAGE_CONTENT for follow-up text.
    """
    parts: list[str] = []
    for line in raw.split("\n"):
        if not line.startswith("data: "):
            continue
        data_str = line[6:]
        if not data_str or data_str == "[DONE]":
            continue
        try:
            data = json.loads(data_str)
        except json.JSONDecodeError:
            continue

        event_type = data.get("type", "")
        if event_type == "CUSTOM" and data.get("name") == "chat_with_data":
            summary = data.get("value", {}).get("summary", {}).get("text", "")
            if summary:
                parts.append(summary)
        elif event_type == "TEXT_MESSAGE_CONTENT":
            delta = data.get("delta", "")
            if delta.strip():
                parts.append(delta)
        elif event_type == "RUN_FINISHED":
            break

    return "\n\n".join(p for p in parts if p.strip())
