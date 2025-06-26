# cskel
🚀 **This project is totally build by Google Gemini-CLI.** 

`cskel` transforms your Python codebase into clean, structured skeletons that preserve essential information while removing implementation details. Perfect for providing LLM context, code reviews, or understanding project architecture. (And maybe tool calling)
> Extract code skeletons with high SNR for LLM analysis - preserve signatures, types, docstrings while minimizing implementation noise

## Features

- 🎯 **High Signal-to-Noise Ratio**: Keep what matters, remove the noise
- 🏗️ **Structure Preservation**: Maintains function signatures, types, and docstrings
- 🎚️ **Flexible Level Control**: Define importance per function with decorators or globally per file, with function-level settings overriding file-level ones.
- 🔍 **Smart Analysis**: Automatically detects important function calls and dependencies
- 🚀 **LLM Optimized**: Reduces context size while preserving semantic meaning
- ⚙️ **Configurable**: Flexible ignore patterns and extraction rules

## Quick Start

### Installation

This project is intended to be run from a local clone. Follow these steps to get started:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/cskel.git
    cd cskel
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
    ```

3.  **Install in editable mode:**
    ```bash
    pip install -e .
    ```
    This will make the `cskel` command available in your terminal. Any changes you make to the source code will be immediately reflected.

### Basic Usage

```python
from cskel import code_level, extract_skeleton

# Mark functions with importance levels
@code_level(3)  # High importance - keep full implementation
def critical_business_logic():
    """Core business logic that must be preserved"""
    return process_important_data()

@code_level(1)  # Low importance - simplify to skeleton
def helper_function(data: List[Dict]) -> DataFrame:
    """Helper function for data processing"""
    # Implementation details removed, but signature preserved
    pass

# Extract project skeleton
extract_skeleton("./src", output_dir="./skeleton", min_level=2)
```

### Command Line

```bash
# Initialize cskel in your project (creates default config files)
cskel init

# Extract a skeleton from a source directory
cskel extract ./src --output ./skeleton --min-level 2

# Preview what the skeleton would look like without writing files
cskel preview ./src

# Analyze your project for statistics on functions, classes, and levels
cskel analyze ./src
```

## How It Works

### What Gets Preserved

✅ **Always Kept**:
- Function signatures and parameters
- Type annotations (input/output)
- Docstrings and comments
- Class definitions and methods
- Import statements
- Module-level variables and constants

✅ **Intelligently Preserved**:
- Important function calls (as comments)
- Exception handling structure
- Conditional logic flow
- Decorator information

❌ **Removed**:
- Implementation details
- Complex logic and algorithms
- Data processing code
- Configuration and setup code (configurable)

### Level System

`cskel` offers flexible control over skeletonization granularity:

-   **Function-level**: Use `@code_level(N)` decorator on individual functions.
-   **File-level**: Define `__code_level__ = N` at the top of a Python file to set a default level for all functions within that file.
-   **Override**: A function's `@code_level` decorator will always override the file-level `__code_level__` setting.

```python
@code_level(1)  # Basic skeleton only
@code_level(2)  # Include key structure
@code_level(3)  # Preserve important logic
@code_level(4)  # Keep full implementation
# No decorator = level 0 (minimal skeleton)
```

### Smart Call Analysis

`cskel` automatically identifies and preserves important function calls as comments by default. This behavior can be toggled via the `preserve_calls_as_comments` configuration.

```python
@code_level(2)
def process_user_data(user_id: str) -> UserProfile:
    """Process user data and return profile"""
    # Important calls detected:
    # → validate_user_id(user_id)
    # → fetch_from_database(user_id) 
    # → transform_profile_data(raw_data)
    pass
```

## Configuration

### .skelignore

Create a `.skelignore` file to exclude files and directories:

```
# Ignore patterns
config/
*.env
test_*
__pycache__/
migrations/
docs/
```

### cskel.toml

Configure extraction behavior:

```toml
[cskel]
min_level = 1
preserve_imports = true
include_private = false
smart_calls = true
max_call_depth = 2
preserve_calls_as_comments = true # New: Whether to preserve function calls as comments (default: true)

[cskel.preserve]
constants = true
type_aliases = true
dataclasses = true
enums = true

[cskel.output]
format = "python"  # or "markdown"
include_metrics = true
add_generation_info = true
```

## Advanced Features

### Type Inference

For code without type annotations, `cskel` can infer types:

```python
# Original code (no types)
def process_data(items):
    return [item.upper() for item in items]

# Generated skeleton with inferred types
def process_data(items: List[str]) -> List[str]:
    """Inferred from usage patterns"""
    pass
```

### Project Analysis

```python
from cskel import analyze_project

# Get project insights
stats = analyze_project("./src")
print(f"Functions: {stats.function_count}")
print(f"Classes: {stats.class_count}")
print(f"Coverage: {stats.level_coverage}")
```

### Integration with Development Tools

```python
# Pre-commit hook
from cskel import validate_levels

# Ensure all public functions have level decorators
validate_levels("./src", require_levels=True)
```

## Examples

### Input Code

```python
import pandas as pd
from typing import List, Dict

@code_level(3)
def analyze_sales_data(file_path: str, filters: Dict) -> pd.DataFrame:
    """Analyze sales data with given filters"""
    # Load raw data
    df = pd.read_csv(file_path)
    
    # Apply filters
    for column, value in filters.items():
        df = df[df[column] == value]
    
    # Complex analysis logic
    df['revenue'] = df['price'] * df['quantity']
    df['profit_margin'] = (df['revenue'] - df['cost']) / df['revenue']
    
    # Statistical calculations
    summary = df.groupby('category').agg({
        'revenue': ['sum', 'mean'],
        'profit_margin': 'mean'
    })
    
    return summary

@code_level(1)  
def format_currency(amount: float) -> str:
    """Format amount as currency string"""
    return f"${amount:,.2f}"
```

### Generated Skeleton

```python
import pandas as pd
from typing import List, Dict

@code_level(3)
def analyze_sales_data(file_path: str, filters: Dict) -> pd.DataFrame:
    """Analyze sales data with given filters"""
    # Important calls: pd.read_csv(), df.groupby(), df.agg()
    # Logic flow: data loading → filtering → analysis → aggregation
    pass

@code_level(1)
def format_currency(amount: float) -> str:
    """Format amount as currency string"""
    pass
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines. The development setup is the same as the installation process described above.

### Running Tests

```bash
pytest
pytest --cov=cskel tests/
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Related Projects

- [LibCST](https://github.com/Instagram/LibCST) - Concrete syntax tree parser
- [Aider](https://github.com/Aider-AI/aider) - AI pair programming
- [Tree-sitter](https://tree-sitter.github.io/) - Language parsing library

---

**Made with ❤️ for developers who want to share clean code context with LLMs**