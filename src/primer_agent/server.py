"""Primer Agent — MCP server for Primer Enterprise Platform (PEP)."""

from mcp.server.fastmcp import FastMCP

from primer_agent.config import PEPConfig
from primer_agent.tools import register_tools
from primer_agent.resources import register_resources
from primer_agent.prompts import register_prompts

mcp = FastMCP(
    "Primer",
    instructions="MCP server for Primer Enterprise Platform — search, workspaces, AI briefings",
)

# Wire up all tools, resources, and prompts
register_tools(mcp)
register_resources(mcp)
register_prompts(mcp)


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
