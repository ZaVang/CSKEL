import libcst as cst
from typing import Dict, List
from dataclasses import dataclass, field

@dataclass
class ProjectStats:
    total_files: int = 0
    total_functions: int = 0
    total_classes: int = 0
    functions_with_level: int = 0
    level_distribution: Dict[int, int] = field(default_factory=lambda: {0:0, 1:0, 2:0, 3:0, 4:0})

    @property
    def level_coverage(self) -> float:
        if self.total_functions == 0:
            return 0.0
        return (self.functions_with_level / self.total_functions) * 100

    def __add__(self, other: 'ProjectStats') -> 'ProjectStats':
        new_dist = self.level_distribution.copy()
        for level, count in other.level_distribution.items():
            new_dist[level] = new_dist.get(level, 0) + count

        return ProjectStats(
            total_files=self.total_files + other.total_files,
            total_functions=self.total_functions + other.total_functions,
            total_classes=self.total_classes + other.total_classes,
            functions_with_level=self.functions_with_level + other.functions_with_level,
            level_distribution=new_dist,
        )

class AnalysisVisitor(cst.CSTVisitor):
    """A visitor to collect statistics about a Python file."""
    def __init__(self) -> None:
        self.stats = ProjectStats(total_files=1)

    def visit_ClassDef(self, node: cst.ClassDef) -> bool:
        self.stats.total_classes += 1
        # Continue visiting inside the class
        return True

    def visit_FunctionDef(self, node: cst.FunctionDef) -> bool:
        self.stats.total_functions += 1
        level = self._get_code_level(node)
        if level > 0:
            self.stats.functions_with_level += 1
        self.stats.level_distribution[level] = self.stats.level_distribution.get(level, 0) + 1
        # Do not visit inside the function, as we don't want to count nested functions here
        return False

    def _get_code_level(self, node: cst.FunctionDef) -> int:
        for decorator in node.decorators:
            if isinstance(decorator.decorator, cst.Call):
                if isinstance(decorator.decorator.func, cst.Name) and decorator.decorator.func.value == "code_level":
                    if decorator.decorator.args:
                        arg = decorator.decorator.args[0].value
                        if isinstance(arg, cst.Integer):
                            return int(arg.value)
        return 0

def analyze_file(code: str) -> ProjectStats:
    """Analyzes a single string of Python code and returns its stats."""
    module = cst.parse_module(code)
    visitor = AnalysisVisitor()
    module.visit(visitor)
    return visitor.stats
