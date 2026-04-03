"""MCP tools for Primer Agent."""

from mcp.server.fastmcp import FastMCP

from primer_agent.tools.create_workspace import register as register_create_workspace
from primer_agent.tools.search import register as register_search
from primer_agent.tools.chat import register as register_chat
from primer_agent.tools.create_briefing import register as register_create_briefing


def register_tools(mcp: FastMCP) -> None:
    register_create_workspace(mcp)
    register_search(mcp)
    register_chat(mcp)
    register_create_briefing(mcp)
