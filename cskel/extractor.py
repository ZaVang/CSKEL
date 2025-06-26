import libcst as cst
from typing import List, Set, Optional

class CommentCollector(cst.CSTVisitor):
    """A visitor to gather all unique comments from a CST node."""
    def __init__(self) -> None:
        self.comments: List[cst.Comment] = []
        self.comment_ids_seen: Set[int] = set()

    def visit_Comment(self, node: cst.Comment) -> None:
        if id(node) not in self.comment_ids_seen:
            self.comments.append(node)
            self.comment_ids_seen.add(id(node))

class CallCollector(cst.CSTVisitor):
    """A visitor to gather all function calls from a CST node."""
    def __init__(self) -> None:
        self.calls: List[cst.Call] = []

    def visit_Call(self, node: cst.Call) -> bool:
        self.calls.append(node)
        return False # Do not visit nested calls

class SkeletonTransformer(cst.CSTTransformer):
    """The core transformer that converts a Python module into a skeleton."""
    def __init__(self, module: cst.Module, min_level: int = 1, file_level: int = 0, preserve_calls: bool = True):
        self.module = module
        self.min_level = min_level
        self.file_level = file_level
        self.preserve_calls = preserve_calls

    def get_code_level(self, node: cst.FunctionDef) -> int:
        """Extracts the integer value from a @code_level(N) decorator."""
        for decorator in node.decorators:
            if isinstance(decorator.decorator, cst.Call):
                if isinstance(decorator.decorator.func, cst.Name) and decorator.decorator.func.value == "code_level":
                    if decorator.decorator.args:
                        arg = decorator.decorator.args[0].value
                        if isinstance(arg, cst.Integer):
                            return int(arg.value)
        return self.file_level

    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.FunctionDef:
        """Processes each function, skeletonizing it if below the min_level."""
        code_level = self.get_code_level(original_node)

        if code_level >= self.min_level:
            return updated_node

        new_body_statements = []

        docstring_stmt = self._get_docstring_statement(original_node)
        if docstring_stmt:
            new_body_statements.append(docstring_stmt)

        if self.preserve_calls:
            call_collector = CallCollector()
            original_node.body.visit(call_collector)

            if call_collector.calls:
                new_body_statements.append(cst.EmptyLine(comment=cst.Comment("# Important calls:")))
                for call_node in call_collector.calls:
                    if isinstance(call_node.func, cst.Name) and call_node.func.value.endswith("Error"):
                        continue
                    try:
                        call_str = self.module.code_for_node(call_node)
                        comment_text = f"# → {call_str}"
                        new_body_statements.append(cst.EmptyLine(comment=cst.Comment(comment_text)))
                    except Exception:
                        pass

        comment_collector = CommentCollector()
        original_node.body.visit(comment_collector)
        if comment_collector.comments:
            if self.preserve_calls and call_collector.calls:
                 new_body_statements.append(cst.EmptyLine())
            for comment in comment_collector.comments:
                new_body_statements.append(cst.EmptyLine(comment=comment))

        new_body_statements.append(cst.SimpleStatementLine(body=[cst.Pass()]))

        return updated_node.with_changes(
            body=cst.IndentedBlock(body=new_body_statements)
        )

    def _get_docstring_statement(self, node: cst.FunctionDef) -> Optional[cst.SimpleStatementLine]:
        """Extracts the docstring from a function, if it exists."""
        if node.body.body:
            first_stmt = node.body.body[0]
            if isinstance(first_stmt, cst.SimpleStatementLine):
                if len(first_stmt.body) == 1 and isinstance(first_stmt.body[0], cst.Expr):
                    value_node = first_stmt.body[0].value
                    if isinstance(value_node, (cst.SimpleString, cst.ConcatenatedString)):
                        return first_stmt
        return None

def _get_file_level(module: cst.Module) -> int:
    """Extracts the file-level code_level, e.g., __code_level__ = 1"""
    for node in module.body:
        if isinstance(node, cst.SimpleStatementLine):
            if len(node.body) == 1 and isinstance(node.body[0], cst.Assign):
                assign = node.body[0]
                if len(assign.targets) == 1 and isinstance(assign.targets[0].target, cst.Name):
                    if assign.targets[0].target.value == "__code_level__":
                        if isinstance(assign.value, cst.Integer):
                            return int(assign.value.value)
    return 0

def create_skeleton(code: str, min_level: int = 1, preserve_calls_as_comments: bool = True) -> str:
    """The main function to create a skeleton from a string of Python code."""
    module = cst.parse_module(code)
    file_level = _get_file_level(module)
    transformer = SkeletonTransformer(
        module=module,
        min_level=min_level,
        file_level=file_level,
        preserve_calls=preserve_calls_as_comments
    )
    modified_tree = module.visit(transformer)
    return modified_tree.code
