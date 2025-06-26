"""
Provides the @code_level decorator for annotating functions.
"""

def code_level(level: int):
    """
    A decorator to mark the importance level of a function or method.

    This decorator does nothing at runtime. It only serves as a static marker
    for the cskel tool to determine which code blocks to preserve.

    Args:
        level: An integer representing the importance (e.g., 1, 2, 3).
    """
    def decorator(func):
        # This is a pass-through decorator.
        # We could attach the level to the function object, but it's not
        # necessary for static analysis with LibCST.
        return func
    return decorator
