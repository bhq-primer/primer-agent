"""MCP prompts for Primer Agent."""

from mcp.server.fastmcp import FastMCP

from primer_agent.prompts.discovery import register as register_discovery
from primer_agent.prompts.actions import register as register_actions


def register_prompts(mcp: FastMCP) -> None:
    register_discovery(mcp)
    register_actions(mcp)
