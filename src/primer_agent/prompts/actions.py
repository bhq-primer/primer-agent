"""Action-oriented prompts — guide multi-step workflows in PEP."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP


def register(mcp: FastMCP) -> None:
    @mcp.prompt()
    def entity_briefing(entity: str) -> str:
        """Research an entity — create workspace, chat to build profile."""
        return (
            f"Research '{entity}' using PEP:\n\n"
            f"1. Use create_workspace to create a workspace named '{entity} Research' "
            f"with a search query for '{entity}' in news sources from the last 30 days.\n"
            f"2. Use chat to ask the workspace agent: "
            f"'Generate a comprehensive profile of {entity} including key affiliations, "
            f"recent quotes, and a summary of recent coverage.'\n"
            f"3. Read pep://workspaces/{{workspace_id}}/narratives to check for narrative themes.\n"
            f"4. Present a structured briefing with: summary, key affiliations, notable quotes, "
            f"and dominant narratives."
        )

    @mcp.prompt()
    def narrative_report(topic: str) -> str:
        """Analyze narratives around a topic."""
        return (
            f"Analyze the narratives around '{topic}':\n\n"
            f"1. Use create_workspace to create a workspace named '{topic} — Narrative Analysis' "
            f"with a search for '{topic}' in social and news sources from the last 14 days, "
            f"max 500 documents.\n"
            f"2. Use chat to ask: 'What are the dominant narratives about {topic}? "
            f"Identify the main themes, claims, and how they relate to each other.'\n"
            f"3. Read pep://workspaces/{{workspace_id}}/narratives for the computed narrative graph.\n"
            f"4. Present: narrative tree with titles, key claims per narrative, "
            f"document counts, and source distribution."
        )

    @mcp.prompt()
    def daily_briefing(topics: str) -> str:
        """Set up a recurring AI briefing on topics."""
        return (
            f"Set up daily AI briefings for: {topics}\n\n"
            f"For each topic:\n"
            f"1. Use create_briefing with the topic as the search query, "
            f"daily schedule at 09:00 UTC, and asset types ['theme-sets', 'rag-v-summary'].\n"
            f"2. Confirm creation and show the briefing details.\n\n"
            f"If briefings already exist (check pep://briefings), mention them and ask "
            f"whether to create additional ones or update existing ones."
        )

    @mcp.prompt()
    def compare_entities(entity_a: str, entity_b: str) -> str:
        """Compare two entities side-by-side."""
        return (
            f"Compare '{entity_a}' and '{entity_b}':\n\n"
            f"1. Use create_workspace to create a workspace named "
            f"'{entity_a} vs {entity_b}' with a boolean search for "
            f"'{entity_a} OR {entity_b}' in news from the last 30 days.\n"
            f"2. Use chat to ask: 'Compare {entity_a} and {entity_b}. "
            f"What are the key differences in how they are covered? "
            f"Who are their main affiliations? What narratives mention them together?'\n"
            f"3. Read narratives and topics from the workspace resources.\n"
            f"4. Present a side-by-side comparison: coverage volume, sentiment, "
            f"key affiliations, dominant narratives, and shared themes."
        )
