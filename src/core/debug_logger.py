print_statements = True
def print_debug(*args, **kwargs):
    """Print debug statements if enabled."""
    if print_statements:
        print(*args, **kwargs)

print_statements2 = False
def print_debug2(*args, **kwargs):
    """Print debug statements if enabled."""
    if print_statements2:
        print(*args, **kwargs)

print_statements3 = False
def print_debug3(*args, **kwargs):
    """Print debug statements if enabled."""
    if print_statements3:
        print(*args, **kwargs)
