"""Tool: chat — Send a message to a workspace conversation agent."""

from __future__ import annotations

import json

from mcp.server.fastmcp import Context, FastMCP

from primer_agent.client import pep_client

# Maps SSE event types to user-friendly progress labels.
_PROGRESS_LABELS: dict[str, str] = {
    "RUN_STARTED": "Agent started...",
    "THINKING_START": "Agent is thinking...",
    "TOOL_CALL_START": "Agent is searching documents...",
    "TOOL_CALL_END": "Processing search results...",
}


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
                await ctx.report_progress(0, 6, "Resolving conversation...")
            workspace = await pep_client.get_workspace(workspace_id)
            conv_ids = workspace.get("conversation_ids", [])
            if not conv_ids:
                return {"error": "No conversations found for this workspace."}
            conversation_id = conv_ids[0]

        # Stream SSE events with live progress updates
        if ctx:
            await ctx.report_progress(1, 6, "Sending message to agent...")

        parts: list[str] = []
        step = 1
        async for line in pep_client.send_message_stream(conversation_id, message):
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

            # Update progress bar on milestone events
            if ctx and event_type in _PROGRESS_LABELS:
                step = min(step + 1, 5)
                await ctx.report_progress(step, 6, _PROGRESS_LABELS[event_type])

            # Update progress on step_label CUSTOM events
            if ctx and event_type == "CUSTOM" and data.get("name") == "step_label":
                label = data.get("value", {}).get("label", "")
                if label:
                    step = min(step + 1, 5)
                    await ctx.report_progress(step, 6, label)

            # Collect main analysis from chat_with_data CUSTOM events
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

        if ctx:
            await ctx.report_progress(6, 6, "Done")

        agent_text = "\n\n".join(p for p in parts if p.strip())

        return {
            "workspace_id": workspace_id,
            "conversation_id": conversation_id,
            "response": agent_text,
        }
