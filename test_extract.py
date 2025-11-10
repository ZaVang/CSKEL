"""Test the extract_skeleton MCP tool."""

import asyncio
import json
from cskel_mcp.tools import extract_skeleton_tool


async def main():
    print("Testing extract_skeleton tool...")
    print()

    # Test extracting from a single file
    result = await extract_skeleton_tool({
        "source_path": "./cskel/decorator.py",
        "min_level": 1,
        "preserve_calls": True
    })

    result_data = json.loads(result)
    print("Single file extraction:")
    print(json.dumps(result_data, indent=2))

    if result_data.get("success"):
        print("\nSkeleton output:")
        print(result_data.get("skeleton", ""))


if __name__ == "__main__":
    asyncio.run(main())
