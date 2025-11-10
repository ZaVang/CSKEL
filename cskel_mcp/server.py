"""
MCP Server for cskel - Code skeleton extraction service.

This module implements the Model Context Protocol server that exposes
cskel functionality as MCP tools.
"""

import asyncio
import logging
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .tools import (
    extract_skeleton_tool,
    preview_skeleton_tool,
    analyze_project_tool,
    get_config_tool,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cskel-mcp")

# Create MCP server instance
app = Server("cskel-mcp")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """
    List all available MCP tools.

    Returns:
        List of Tool definitions for cskel functionality.
    """
    return [
        Tool(
            name="extract_skeleton",
            description=(
                "Extract code skeleton from Python source code or directory. "
                "Preserves function signatures, types, docstrings while removing "
                "implementation details based on @code_level decorators."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "source_path": {
                        "type": "string",
                        "description": "Path to Python file or directory to process",
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Path where skeleton output should be saved (optional for single files)",
                    },
                    "min_level": {
                        "type": "number",
                        "description": "Minimum code_level to preserve full implementation (default: 1)",
                        "default": 1,
                    },
                    "preserve_calls": {
                        "type": "boolean",
                        "description": "Whether to preserve function calls as comments (default: true)",
                        "default": True,
                    },
                },
                "required": ["source_path"],
            },
        ),
        Tool(
            name="preview_skeleton",
            description=(
                "Preview skeleton transformation of Python code without writing files. "
                "Returns the skeletonized version of the provided code."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "source_code": {
                        "type": "string",
                        "description": "Python source code to preview",
                    },
                    "min_level": {
                        "type": "number",
                        "description": "Minimum code_level to preserve full implementation (default: 1)",
                        "default": 1,
                    },
                    "preserve_calls": {
                        "type": "boolean",
                        "description": "Whether to preserve function calls as comments (default: true)",
                        "default": True,
                    },
                },
                "required": ["source_code"],
            },
        ),
        Tool(
            name="analyze_project",
            description=(
                "Analyze a Python project and return statistics about functions, "
                "classes, and code_level coverage."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "source_path": {
                        "type": "string",
                        "description": "Path to Python file or directory to analyze",
                    },
                },
                "required": ["source_path"],
            },
        ),
        Tool(
            name="get_config",
            description=(
                "Get current cskel configuration from cskel.toml and .skelignore files. "
                "Returns configuration settings and ignore patterns."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "project_root": {
                        "type": "string",
                        "description": "Project root directory (default: current directory)",
                    },
                },
                "required": [],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """
    Handle tool execution requests.

    Args:
        name: Name of the tool to execute
        arguments: Tool-specific arguments

    Returns:
        List of TextContent with tool execution results
    """
    logger.info(f"Calling tool: {name} with arguments: {arguments}")

    try:
        if name == "extract_skeleton":
            result = await extract_skeleton_tool(arguments)
        elif name == "preview_skeleton":
            result = await preview_skeleton_tool(arguments)
        elif name == "analyze_project":
            result = await analyze_project_tool(arguments)
        elif name == "get_config":
            result = await get_config_tool(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")

        return [TextContent(type="text", text=result)]

    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}", exc_info=True)
        error_message = f"Error executing {name}: {str(e)}"
        return [TextContent(type="text", text=error_message)]


async def run_server():
    """Run the MCP server using stdio transport."""
    async with stdio_server() as (read_stream, write_stream):
        logger.info("cskel MCP server starting...")
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )


def main():
    """Main entry point for the MCP server."""
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
