import inspect

print_statements = True
def print_debug(*args, **kwargs):
    """Print debug statements if enabled."""
    if print_statements:
        caller_frame = inspect.currentframe().f_back
        caller_module = inspect.getmodule(caller_frame).__name__
        print(f"({caller_module})", *args, **kwargs)

print_statements2 = False
def print_debug2(*args, **kwargs):
    """Print debug statements if enabled."""
    if print_statements2:
        caller_frame = inspect.currentframe().f_back
        caller_module = inspect.getmodule(caller_frame).__name__
        print(f"({caller_module})", *args, **kwargs)

print_statements3 = False
def print_debug3(*args, **kwargs):
    """Print debug statements if enabled."""
    if print_statements3:
        caller_frame = inspect.currentframe().f_back
        caller_module = inspect.getmodule(caller_frame).__name__
        print(f"({caller_module})", *args, **kwargs)
