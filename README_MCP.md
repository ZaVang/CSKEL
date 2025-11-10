# cskel MCP Service

**Model Context Protocol (MCP) service for code skeleton extraction**

This MCP server exposes cskel's functionality as standardized tools that can be used by LLMs like Claude to extract code skeletons, analyze projects, and preview transformations.

## What is MCP?

The Model Context Protocol (MCP) is a standard protocol for connecting AI assistants to data sources and tools. This allows LLMs to interact with cskel programmatically through a well-defined interface.

## Features

The cskel MCP server provides four main tools:

### 1. `extract_skeleton`
Extract code skeleton from Python source files or directories.

**Parameters:**
- `source_path` (required): Path to Python file or directory
- `output_path` (optional): Where to save skeleton output
- `min_level` (optional, default: 1): Minimum code_level to preserve full implementation
- `preserve_calls` (optional, default: true): Preserve function calls as comments

**Example:**
```json
{
  "source_path": "./my_project/src",
  "output_path": "./my_project/skeleton",
  "min_level": 2,
  "preserve_calls": true
}
```

### 2. `preview_skeleton`
Preview skeleton transformation without writing files.

**Parameters:**
- `source_code` (required): Python source code to preview
- `min_level` (optional, default: 1): Minimum code_level threshold
- `preserve_calls` (optional, default: true): Preserve function calls

**Example:**
```json
{
  "source_code": "def example():\n    return 42",
  "min_level": 1
}
```

### 3. `analyze_project`
Analyze Python project for statistics.

**Parameters:**
- `source_path` (required): Path to Python file or directory

**Returns:**
- Total files, classes, functions
- Code level coverage and distribution

**Example:**
```json
{
  "source_path": "./my_project"
}
```

### 4. `get_config`
Get current cskel configuration.

**Parameters:**
- `project_root` (optional): Project root directory (default: current directory)

**Returns:**
- Configuration settings from cskel.toml
- Ignore patterns from .skelignore

**Example:**
```json
{
  "project_root": "./my_project"
}
```

## Installation

1. **Install the package with MCP support:**

```bash
cd /path/to/CSKEL
pip install -e .
```

This will install both the `cskel` CLI and `cskel-mcp` MCP server.

2. **Verify installation:**

```bash
cskel --version
cskel-mcp --help  # Should show MCP server info
```

## Configuration

### For Claude Desktop

Add to your Claude Desktop configuration file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "cskel": {
      "command": "cskel-mcp",
      "args": [],
      "env": {}
    }
  }
}
```

### For Custom Integrations

If integrating with your own MCP client:

```python
from mcp import ClientSession
from mcp.client.stdio import stdio_client

# Connect to cskel MCP server
async with stdio_client(["cskel-mcp"]) as (read, write):
    async with ClientSession(read, write) as session:
        # Initialize
        await session.initialize()

        # Call tools
        result = await session.call_tool(
            "extract_skeleton",
            arguments={
                "source_path": "./my_code.py",
                "min_level": 2
            }
        )
        print(result)
```

## Usage Examples

### Example 1: Extract Skeleton via Claude

Once configured, you can ask Claude:

> "Use the cskel tool to extract a skeleton from my Python project at ./src with min_level 2"

Claude will call the `extract_skeleton` tool with appropriate parameters.

### Example 2: Analyze Code Coverage

> "Analyze my Python project at ./my_app and tell me the code_level coverage"

Claude will use the `analyze_project` tool to get statistics.

### Example 3: Preview Transformation

> "Show me what this Python function would look like as a skeleton"

Claude can use `preview_skeleton` to show the transformation inline.

## Development

### Running the Server Directly

For testing and development:

```bash
# Run the MCP server
python -m cskel_mcp.server

# Or use the installed command
cskel-mcp
```

The server uses stdio for communication and will wait for MCP protocol messages.

### Testing with MCP Inspector

Use the official MCP Inspector for testing:

```bash
npx @modelcontextprotocol/inspector cskel-mcp
```

This provides a web UI to test all tools interactively.

## Architecture

```
cskel-mcp/
├── server.py          # MCP server implementation
├── tools.py           # Tool implementations
└── __init__.py        # Package initialization

Integration with existing cskel:
├── cskel/
│   ├── extractor.py   # Core skeleton extraction
│   ├── analyzer.py    # Project analysis
│   ├── config.py      # Configuration handling
│   └── ...
```

The MCP server wraps the existing cskel functionality without modifying the core library, maintaining backward compatibility with the CLI.

## Response Format

All tools return JSON responses with a consistent structure:

**Success:**
```json
{
  "success": true,
  "message": "...",
  "data": { ... }
}
```

**Error:**
```json
{
  "success": false,
  "error": "Error description"
}
```

## Troubleshooting

### Server won't start

- Ensure all dependencies are installed: `pip install -e .`
- Check Python version (requires Python 3.8+)
- Verify MCP package is installed: `pip show mcp`

### Tools not appearing in Claude

- Restart Claude Desktop after configuration changes
- Check configuration file path is correct
- Verify JSON syntax in config file

### Permission errors

- Ensure the server has read/write permissions for source and output paths
- Check that paths are absolute or relative to the correct working directory

## Contributing

The MCP server is part of the cskel project. For contributions:

1. Follow the existing code style
2. Add tests for new functionality
3. Update this documentation
4. Submit a pull request

## License

MIT License - same as the main cskel project.

## Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [cskel GitHub](https://github.com/your-username/cskel)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

---

**Made with ❤️ for seamless LLM integration with code skeleton extraction**
