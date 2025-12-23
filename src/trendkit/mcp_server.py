"""
MCP Server for trendkit.

Run with: trendkit-mcp
Or configure in Claude Desktop settings.
"""

import json
from typing import Any

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError:
    raise ImportError("MCP not installed. Run: pip install trendkit[mcp]")

from . import trending, trending_bulk, interest, related, compare


# Create MCP server
server = Server("trendkit")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="trends_trending",
            description="Get realtime trending keywords. Returns list of trending search terms.",
            inputSchema={
                "type": "object",
                "properties": {
                    "geo": {
                        "type": "string",
                        "description": "Country code (KR, US, JP, etc.)",
                        "default": "KR",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of results (max 20)",
                        "default": 10,
                    },
                    "format": {
                        "type": "string",
                        "enum": ["minimal", "standard", "full"],
                        "description": "Output detail level",
                        "default": "minimal",
                    },
                },
            },
        ),
        Tool(
            name="trends_related",
            description="Get related search queries for a keyword.",
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "Target keyword to find related queries",
                    },
                    "geo": {
                        "type": "string",
                        "description": "Country code",
                        "default": "KR",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of results",
                        "default": 10,
                    },
                },
                "required": ["keyword"],
            },
        ),
        Tool(
            name="trends_compare",
            description="Compare keywords by average search interest.",
            inputSchema={
                "type": "object",
                "properties": {
                    "keywords": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Keywords to compare (max 5)",
                    },
                    "geo": {
                        "type": "string",
                        "description": "Country code",
                        "default": "KR",
                    },
                    "days": {
                        "type": "integer",
                        "description": "Time period in days",
                        "default": 90,
                    },
                },
                "required": ["keywords"],
            },
        ),
        Tool(
            name="trends_interest",
            description="Get interest over time for keywords (time series data).",
            inputSchema={
                "type": "object",
                "properties": {
                    "keywords": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Keywords to analyze (max 5)",
                    },
                    "geo": {
                        "type": "string",
                        "description": "Country code",
                        "default": "KR",
                    },
                    "days": {
                        "type": "integer",
                        "description": "Time period in days (1, 7, 30, 90, 365)",
                        "default": 7,
                    },
                },
                "required": ["keywords"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    try:
        if name == "trends_trending":
            result = trending(
                geo=arguments.get("geo", "KR"),
                limit=arguments.get("limit", 10),
                format=arguments.get("format", "minimal"),
            )
        elif name == "trends_related":
            result = related(
                keyword=arguments["keyword"],
                geo=arguments.get("geo", "KR"),
                limit=arguments.get("limit", 10),
            )
        elif name == "trends_compare":
            result = compare(
                keywords=arguments["keywords"],
                geo=arguments.get("geo", "KR"),
                days=arguments.get("days", 90),
            )
        elif name == "trends_interest":
            result = interest(
                keywords=arguments["keywords"],
                geo=arguments.get("geo", "KR"),
                days=arguments.get("days", 7),
            )
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]

    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def _run():
    """Run MCP server (async)."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main():
    """Entry point for MCP server."""
    import asyncio
    asyncio.run(_run())


if __name__ == "__main__":
    main()
