from pathlib import Path


def find_git_root() -> Path:
    """Find the root of the git repository

    Returns:
        root_path (Path): The root of the git repository
    """
    root_path = Path(__file__).parent
    max_depth = 50
    while root_path.is_dir() and not (root_path / ".git").exists() and max_depth > 0:
        root_path = root_path.parent
        max_depth -= 1
    if not (root_path / ".git").exists():
        raise RuntimeError("Could not find git root")
    return root_path
