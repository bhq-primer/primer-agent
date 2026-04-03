"""MCP resources for Primer Agent."""

from mcp.server.fastmcp import FastMCP

from primer_agent.resources.config import register as register_config
from primer_agent.resources.workspaces import register as register_workspaces
from primer_agent.resources.documents import register as register_documents
from primer_agent.resources.briefings import register as register_briefings


def register_resources(mcp: FastMCP) -> None:
    register_config(mcp)
    register_workspaces(mcp)
    register_documents(mcp)
    register_briefings(mcp)
