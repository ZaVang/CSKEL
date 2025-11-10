"""
Simple test script to verify MCP tools functionality.
"""

import asyncio
import json
from pathlib import Path
from cskel_mcp.tools import (
    preview_skeleton_tool,
    analyze_project_tool,
    get_config_tool,
)


async def test_preview_skeleton():
    """Test the preview_skeleton tool."""
    print("Testing preview_skeleton tool...")

    test_code = '''
from cskel import code_level

@code_level(3)
def important_function(x: int, y: int) -> int:
    """This is an important function."""
    result = x + y
    return result * 2

@code_level(1)
def helper_function(data: list) -> dict:
    """Helper function."""
    processed = []
    for item in data:
        processed.append(item.upper())
    return {"processed": processed}
'''

    result = await preview_skeleton_tool({
        "source_code": test_code,
        "min_level": 2,
        "preserve_calls": True
    })

    print("Result:")
    print(result)
    print()


async def test_analyze_project():
    """Test the analyze_project tool."""
    print("Testing analyze_project tool...")

    # Analyze the cskel package itself
    result = await analyze_project_tool({
        "source_path": "./cskel"
    })

    print("Result:")
    print(result)
    print()


async def test_get_config():
    """Test the get_config tool."""
    print("Testing get_config tool...")

    result = await get_config_tool({
        "project_root": "."
    })

    print("Result:")
    print(result)
    print()


async def main():
    """Run all tests."""
    print("=" * 60)
    print("MCP Tools Test Suite")
    print("=" * 60)
    print()

    try:
        await test_preview_skeleton()
        await test_analyze_project()
        await test_get_config()

        print("=" * 60)
        print("All tests completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
