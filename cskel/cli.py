"""
This module defines the command-line interface (CLI) for cskel.

It uses the Typer library to create a clean, modern CLI with subcommands
for the main functionalities: extract, init, preview, and analyze.
"""
import typer
from pathlib import Path
import typing

from .extractor import create_skeleton
from .analyzer import ProjectStats, analyze_file
from .config import Config

# Create a Typer app. Using a function helps with testing and isolation.
def get_app():
    app = typer.Typer(
        name="cskel",
        help="Extract code skeletons with high SNR for LLM analysis.",
        add_completion=False,
    )

    @app.command()
    def extract(
        source_dir: Path = typer.Argument(
            ...,
            exists=True,
            file_okay=False,
            dir_okay=True,
            readable=True,
            resolve_path=True,
            help="Source directory to process.",
        ),
        output_dir: Path = typer.Option(
            ...,
            "--output",
            "-o",
            help="Directory to save the skeleton files.",
            resolve_path=True,
        ),
        min_level: int = typer.Option(
            None, # Default to None, so we can use the config value
            "--min-level",
            help="The minimum code level to preserve full implementation.",
        ),
    ):
        """
        Extracts a code skeleton from a Python project.
        """
        project_root = Path.cwd()
        config = Config(project_root)

        # CLI option overrides config file
        final_min_level = min_level if min_level is not None else config.get("min_level")

        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)
        elif not output_dir.is_dir():
            typer.secho(f"Error: Output path {output_dir} exists and is not a directory.", fg=typer.colors.RED)
            raise typer.Exit(1)

        typer.echo(f"Scanning {source_dir} using min-level: {final_min_level}...")
        
        files_to_process = []
        for path in source_dir.rglob("*.py"):
            if not config.should_ignore(path):
                files_to_process.append(path)

        file_count = 0
        for source_file in files_to_process:
            relative_path = source_file.relative_to(source_dir)
            output_file = output_dir / relative_path

            output_file.parent.mkdir(parents=True, exist_ok=True)

            typer.echo(f"  -> Processing: {relative_path}")

            try:
                source_code = source_file.read_text(encoding="utf-8")
                skeleton_code = create_skeleton(source_code, min_level=final_min_level)
                output_file.write_text(skeleton_code, encoding="utf-8")
                file_count += 1
            except Exception as e:
                typer.secho(f"    Error processing {source_file.name}: {e}", fg=typer.colors.RED)
        
        typer.secho(f"\nSuccessfully processed {file_count} file(s).", fg=typer.colors.GREEN)

    @app.command()
    def init():
        """Initializes cskel configuration files in the current directory."""
        project_root = Path.cwd()
        cskel_toml_path = project_root / "cskel.toml"
        skelignore_path = project_root / ".skelignore"

        # Default cskel.toml content
        CSKEL_TOML_CONTENT = '''
# cskel configuration file

[cskel]
# The minimum importance level for a function to have its full implementation preserved.
# Functions with a level below this will be skeletonized.
# Default is 1.
min_level = 1
'''

        # Default .skelignore content
        SKELIGNORE_CONTENT = '''
# Patterns for files and directories to ignore during skeleton extraction.
# Uses .gitignore syntax.

# Python cache
__pycache__/
*.pyc

# Virtual environment
.venv/
virtualenv/
env/

# Test files
tests/
test_*.py
*_test.py
'''

        if cskel_toml_path.exists():
            typer.secho("cskel.toml already exists.", fg=typer.colors.YELLOW)
        else:
            cskel_toml_path.write_text(CSKEL_TOML_CONTENT)
            typer.secho("Created cskel.toml", fg=typer.colors.GREEN)

        if skelignore_path.exists():
            typer.secho(".skelignore already exists.", fg=typer.colors.YELLOW)
        else:
            skelignore_path.write_text(SKELIGNORE_CONTENT)
            typer.secho("Created .skelignore", fg=typer.colors.GREEN)

    @app.command()
    def preview(
        source_dir: Path = typer.Argument(
            ...,
            exists=True,
            file_okay=False,
            dir_okay=True,
            readable=True,
            resolve_path=True,
            help="Source directory to preview.",
        ),
        min_level: int = typer.Option(
            None,
            "--min-level",
            help="The minimum code level to preserve full implementation.",
        ),
    ):
        """Previews the skeletonization of a Python project without writing files."""
        project_root = Path.cwd()
        config = Config(project_root)

        final_min_level = min_level if min_level is not None else config.get("min_level")

        typer.echo(f"Previewing skeleton for {source_dir} using min-level: {final_min_level}...")

        files_to_process = []
        for path in source_dir.rglob("*.py"):
            if not config.should_ignore(path):
                files_to_process.append(path)

        for source_file in files_to_process:
            relative_path = source_file.relative_to(project_root)
            typer.secho(f"--- {relative_path} ---", fg=typer.colors.YELLOW)
            try:
                source_code = source_file.read_text(encoding="utf-8")
                skeleton_code = create_skeleton(source_code, min_level=final_min_level)
                typer.echo(skeleton_code)
            except Exception as e:
                typer.secho(f"Error processing {source_file.name}: {e}", fg=typer.colors.RED)

    @app.command()
    def analyze(
        source_dir: Path = typer.Argument(
            ...,
            exists=True,
            file_okay=False,
            dir_okay=True,
            readable=True,
            resolve_path=True,
            help="Source directory to analyze.",
        ),
    ):
        """Analyzes the codebase to provide statistics and insights."""
        project_root = Path.cwd()
        config = Config(project_root)
        
        typer.echo(f"Analyzing {source_dir}...")

        files_to_process = []
        for path in source_dir.rglob("*.py"):
            if not config.should_ignore(path):
                files_to_process.append(path)

        total_stats = ProjectStats()
        for source_file in files_to_process:
            try:
                source_code = source_file.read_text(encoding="utf-8")
                stats = analyze_file(source_code)
                total_stats += stats
            except Exception as e:
                typer.secho(f"Could not analyze {source_file.name}: {e}", fg=typer.colors.RED)

        # --- Display Results ---
        typer.echo("\n--- Project Analysis ---")
        typer.echo(f"Total Files Scanned: {total_stats.total_files}")
        typer.echo(f"Total Classes Found: {total_stats.total_classes}")
        typer.echo(f"Total Functions Found: {total_stats.total_functions}")
        typer.echo(f"- Functions with @code_level: {total_stats.functions_with_level}")
        typer.echo(f"- Coverage: {total_stats.level_coverage:.2f}%")
        
        typer.echo("\n--- Level Distribution ---")
        for level, count in sorted(total_stats.level_distribution.items()):
            if count > 0:
                typer.echo(f"  Level {level}: {count} function(s)")

    @app.callback()
    def main(
        version: typing.Optional[bool] = typer.Option(
            None, "--version", help="Show the version and exit.", is_eager=True
        )
    ):
        """
        cskel helps you extract clean code skeletons.
        """
        if version:
            print("cskel 0.0.1")
            raise typer.Exit()

    return app

app = get_app()

if __name__ == "__main__":
    app()