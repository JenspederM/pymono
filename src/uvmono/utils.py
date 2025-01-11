from pathlib import Path
import shutil
import subprocess


def find_git_root(root=__file__) -> Path:
    """Find the root of the git repository

    Returns:
        root_path (Path): The root of the git repository
    """
    root_path = Path(root).parent
    max_depth = 50
    while root_path.is_dir() and not (root_path / ".git").exists() and max_depth > 0:
        root_path = root_path.parent
        max_depth -= 1
    if not (root_path / ".git").exists():
        raise RuntimeError("Could not find git root")
    return root_path


def has_uv():
    """Check if `uv` is installed"""
    has_uv = shutil.which("uv") or subprocess.run(["uv", "--version"]).returncode == 0
    if not has_uv:
        msg = """`uv` not found.

        This package requires the `uv` command line tool.

        You can find information on how to install it here:
            https://docs.astral.sh/uv/getting-started/installation/ 
        """
        raise RuntimeError(msg)
    return True
