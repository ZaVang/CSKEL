"""
MCP Tool implementations for cskel.

This module contains the actual implementation logic for each MCP tool.
"""

import json
from pathlib import Path
from typing import Any, Dict

from cskel.extractor import create_skeleton
from cskel.analyzer import analyze_file, ProjectStats
from cskel.config import Config


async def extract_skeleton_tool(arguments: Dict[str, Any]) -> str:
    """
    Extract skeleton from a Python file or directory.

    Args:
        arguments: Dictionary containing:
            - source_path: Path to source file/directory
            - output_path: Optional output path
            - min_level: Minimum code level (default: 1)
            - preserve_calls: Whether to preserve calls as comments (default: True)

    Returns:
        JSON string with extraction results
    """
    source_path = Path(arguments["source_path"]).resolve()
    output_path = arguments.get("output_path")
    min_level = arguments.get("min_level", 1)
    preserve_calls = arguments.get("preserve_calls", True)

    if not source_path.exists():
        return json.dumps({
            "success": False,
            "error": f"Source path does not exist: {source_path}"
        })

    # Load configuration from project root
    project_root = source_path if source_path.is_dir() else source_path.parent
    config = Config(project_root)

    # Handle single file
    if source_path.is_file():
        if not source_path.suffix == ".py":
            return json.dumps({
                "success": False,
                "error": f"Source must be a Python file (.py): {source_path}"
            })

        try:
            source_code = source_path.read_text(encoding="utf-8")
            skeleton_code = create_skeleton(
                source_code,
                min_level=min_level,
                preserve_calls_as_comments=preserve_calls
            )

            # If output_path provided, write to file
            if output_path:
                output_file = Path(output_path).resolve()
                output_file.parent.mkdir(parents=True, exist_ok=True)
                output_file.write_text(skeleton_code, encoding="utf-8")

                return json.dumps({
                    "success": True,
                    "message": f"Skeleton written to {output_file}",
                    "files_processed": 1,
                    "output_path": str(output_file)
                })
            else:
                # Return the skeleton code directly
                return json.dumps({
                    "success": True,
                    "skeleton": skeleton_code,
                    "files_processed": 1
                })

        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Error processing file: {str(e)}"
            })

    # Handle directory
    elif source_path.is_dir():
        if not output_path:
            return json.dumps({
                "success": False,
                "error": "output_path is required when processing a directory"
            })

        output_dir = Path(output_path).resolve()
        output_dir.mkdir(parents=True, exist_ok=True)

        files_to_process = []
        for path in source_path.rglob("*.py"):
            if not config.should_ignore(path):
                files_to_process.append(path)

        processed_count = 0
        errors = []

        for source_file in files_to_process:
            try:
                relative_path = source_file.relative_to(source_path)
                output_file = output_dir / relative_path
                output_file.parent.mkdir(parents=True, exist_ok=True)

                source_code = source_file.read_text(encoding="utf-8")
                skeleton_code = create_skeleton(
                    source_code,
                    min_level=min_level,
                    preserve_calls_as_comments=preserve_calls
                )
                output_file.write_text(skeleton_code, encoding="utf-8")
                processed_count += 1

            except Exception as e:
                errors.append({
                    "file": str(source_file),
                    "error": str(e)
                })

        result = {
            "success": True,
            "message": f"Processed {processed_count} file(s)",
            "files_processed": processed_count,
            "output_path": str(output_dir)
        }

        if errors:
            result["errors"] = errors

        return json.dumps(result, indent=2)

    else:
        return json.dumps({
            "success": False,
            "error": f"Invalid source path: {source_path}"
        })


async def preview_skeleton_tool(arguments: Dict[str, Any]) -> str:
    """
    Preview skeleton transformation of Python code.

    Args:
        arguments: Dictionary containing:
            - source_code: Python source code string
            - min_level: Minimum code level (default: 1)
            - preserve_calls: Whether to preserve calls as comments (default: True)

    Returns:
        The skeletonized code as a string
    """
    source_code = arguments.get("source_code", "")
    min_level = arguments.get("min_level", 1)
    preserve_calls = arguments.get("preserve_calls", True)

    if not source_code:
        return json.dumps({
            "success": False,
            "error": "source_code is required"
        })

    try:
        skeleton_code = create_skeleton(
            source_code,
            min_level=min_level,
            preserve_calls_as_comments=preserve_calls
        )

        return json.dumps({
            "success": True,
            "original_length": len(source_code),
            "skeleton_length": len(skeleton_code),
            "reduction_ratio": f"{(1 - len(skeleton_code) / len(source_code)) * 100:.1f}%",
            "skeleton": skeleton_code
        }, indent=2)

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Error creating skeleton: {str(e)}"
        })


async def analyze_project_tool(arguments: Dict[str, Any]) -> str:
    """
    Analyze a Python project for statistics.

    Args:
        arguments: Dictionary containing:
            - source_path: Path to Python file or directory

    Returns:
        JSON string with project statistics
    """
    source_path = Path(arguments["source_path"]).resolve()

    if not source_path.exists():
        return json.dumps({
            "success": False,
            "error": f"Source path does not exist: {source_path}"
        })

    # Load configuration
    project_root = source_path if source_path.is_dir() else source_path.parent
    config = Config(project_root)

    total_stats = ProjectStats()

    # Handle single file
    if source_path.is_file():
        if not source_path.suffix == ".py":
            return json.dumps({
                "success": False,
                "error": f"Source must be a Python file (.py): {source_path}"
            })

        try:
            source_code = source_path.read_text(encoding="utf-8")
            stats = analyze_file(source_code)
            total_stats += stats

        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"Error analyzing file: {str(e)}"
            })

    # Handle directory
    elif source_path.is_dir():
        files_to_process = []
        for path in source_path.rglob("*.py"):
            if not config.should_ignore(path):
                files_to_process.append(path)

        errors = []
        for source_file in files_to_process:
            try:
                source_code = source_file.read_text(encoding="utf-8")
                stats = analyze_file(source_code)
                total_stats += stats
            except Exception as e:
                errors.append({
                    "file": str(source_file),
                    "error": str(e)
                })

    # Format results
    result = {
        "success": True,
        "analysis": {
            "total_files": total_stats.total_files,
            "total_classes": total_stats.total_classes,
            "total_functions": total_stats.total_functions,
            "functions_with_level": total_stats.functions_with_level,
            "level_coverage": f"{total_stats.level_coverage:.2f}%",
            "level_distribution": {
                f"level_{k}": v
                for k, v in sorted(total_stats.level_distribution.items())
                if v > 0
            }
        }
    }

    return json.dumps(result, indent=2)


async def get_config_tool(arguments: Dict[str, Any]) -> str:
    """
    Get current cskel configuration.

    Args:
        arguments: Dictionary containing:
            - project_root: Optional project root path

    Returns:
        JSON string with configuration settings
    """
    project_root = arguments.get("project_root")

    if project_root:
        root_path = Path(project_root).resolve()
    else:
        root_path = Path.cwd()

    if not root_path.exists() or not root_path.is_dir():
        return json.dumps({
            "success": False,
            "error": f"Invalid project root: {root_path}"
        })

    try:
        config = Config(root_path)

        # Read .skelignore patterns
        ignore_patterns = []
        if config.skelignore_path.exists():
            ignore_patterns = config.skelignore_path.read_text(encoding="utf-8").splitlines()

        result = {
            "success": True,
            "project_root": str(root_path),
            "config_file": str(config.cskel_toml_path) if config.cskel_toml_path.exists() else None,
            "ignore_file": str(config.skelignore_path) if config.skelignore_path.exists() else None,
            "settings": config.settings,
            "ignore_patterns": [p for p in ignore_patterns if p.strip() and not p.strip().startswith("#")]
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Error loading configuration: {str(e)}"
        })
