# How to Use cskel

`cskel` is a powerful command-line tool designed to help you extract clean, high-level skeletons from your Python codebase. This guide will walk you through the installation, core concepts, and detailed usage of each command.

## Installation

To get started, install `cskel` using pip:

```bash
pip install cskel
```

This will make the `cskel` command available in your terminal.

## Core Concept: Code Levels

The central idea behind `cskel` is the concept of "code levels". You annotate your functions with a special decorator, `@code_level(N)`, to assign them an importance level.

- **`@code_level(1)`**: A function with basic importance. It might be a helper or a utility function.
- **`@code_level(2)`**: A function with moderate importance, perhaps a key part of a feature.
- **`@code_level(3)` or higher**: A function with critical importance, such as core business logic that must be preserved.

When you run `cskel`, you provide a `--min-level`. Any function with a `@code_level` **below** this minimum will be "skeletonized"—its implementation will be replaced with a `pass` statement, while its signature, docstring, and important internal calls are preserved.

**If a function has no `@code_level` decorator, it is treated as `level 0`** and will almost always be skeletonized, which is the desired default behavior.

## Command-Line Interface (CLI)

`cskel` provides four main commands: `init`, `extract`, `preview`, and `analyze`.

### 1. `cskel init`

This is the best command to start with in a new project. It creates the default configuration files for you.

**Usage:**
```bash
cskel init
```

**What it does:**
- Creates a `cskel.toml` file with default settings. This is where you can set a project-wide `min_level`.
- Creates a `.skelignore` file, which works just like `.gitignore`. You can add files and directories to this file to exclude them from processing.

### 2. `cskel extract`

This is the main command for generating the code skeleton.

**Usage:**
```bash
cskel extract <SOURCE_DIRECTORY> --output <OUTPUT_DIRECTORY> [--min-level N]
```

**Arguments & Options:**
- **`SOURCE_DIRECTORY`**: The path to the Python project you want to process (e.g., `./src`).
- **`--output <path>`** (or `-o <path>`): The directory where the generated skeleton files will be saved.
- **`--min-level <N>`** (optional): Overrides the `min_level` set in `cskel.toml`. This lets you dynamically control the granularity of the skeleton.

**Example:**
```bash
# Extract a skeleton from the 'src' folder and save it to 'skeleton'
# Only preserve the full implementation of functions at level 2 or higher.
cskel extract ./src --output ./skeleton --min-level 2
```

### 3. `cskel preview`

This command lets you see what the skeleton would look like without actually creating any files. It prints the results directly to the console.

**Usage:**
```bash
cskel preview <SOURCE_DIRECTORY> [--min-level N]
```

**Example:**
```bash
# Preview the skeleton for the 'src' directory with a min-level of 1
cskel preview ./src --min-level 1
```

### 4. `cskel analyze`

This command scans your codebase and provides useful statistics about your functions, classes, and how extensively you've used the `@code_level` decorator.

**Usage:**
```bash
cskel analyze <SOURCE_DIRECTORY>
```

**Example Output:**
```
--- Project Analysis ---
Total Files Scanned: 10
Total Classes Found: 5
Total Functions Found: 42
- Functions with @code_level: 18
- Coverage: 42.86%

--- Level Distribution ---
  Level 0: 24 function(s)
  Level 1: 10 function(s)
  Level 2: 5 function(s)
  Level 3: 3 function(s)
```

## A Practical Workflow

Here’s how you might use `cskel` on your project:

1.  **Initialize**:
    ```bash
    cd your-project
    cskel init
    ```

2.  **Annotate**: Go through your codebase and add the `@code_level` decorator to your functions. Remember to import it first:
    ```python
    from cskel import code_level

    @code_level(3)
    def core_business_logic():
        # ...

    @code_level(1)
    def helper_function():
        # ...
    ```

3.  **Configure**: Edit `.skelignore` to exclude any directories you don't want to process, such as `tests/` or `docs/`.

4.  **Preview**: Run the `preview` command to see if the output matches your expectations.
    ```bash
    cskel preview ./your_source_code --min-level 2
    ```

5.  **Extract**: Once you are satisfied, run the `extract` command to generate the final skeleton files.
    ```bash
    cskel extract ./your_source_code --output ./skeleton --min-level 2
    ```

You now have a clean, high-level representation of your project in the `./skeleton` directory, perfect for sharing with LLMs or for code review.
