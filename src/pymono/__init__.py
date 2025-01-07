import subprocess
import fire

from pymono.github import find_projects, get_includes, set_github_output
from pymono.template import add_project_standards
from pymono.utils import find_git_root, has_uv


class PyMono:
    """PyMono is a tool to help manage mono-repos in python"""

    def __init__(self):
        self._root = find_git_root()
        self._packages_root = self._root / "packages"
        self._packages = [p for p in self._packages_root.iterdir() if p.is_dir()]

    def new(self, package_name: str):
        """Create a new package in the mono-repo.

        Args:
            package_name (str): The name of the package to create.
        """
        has_uv()
        package_dir = self._packages_root / package_name
        if package_dir.exists():
            raise FileExistsError(f"Package {package_name} already exists")
        package_dir.mkdir()
        dir_cmd = ["--directory", str(package_dir)]
        default_packages = ["pytest", "pytest-cov"]
        subprocess.run(["uv", "init", "--package", *dir_cmd])
        assert (
            package_dir / "pyproject.toml"
        ).exists(), f"Failed to create package: {package_name}"
        add_project_standards(package_dir)
        subprocess.run(["uv", "add", *default_packages, "--dev", *dir_cmd])

    def list(self):
        """List the packages in the mono-repo"""
        packages = [p.name for p in self._packages_root.iterdir() if p.is_dir()]
        return sorted(packages)

    def _get_relative_package_path(self, package_name: str):
        """Get the path to the package"""
        package_path = self._packages_root / package_name
        if not package_path.exists():
            raise FileNotFoundError(f"Package {package_name} not found")
        return package_path.relative_to(self._packages_root.parent).as_posix()

    def matrix_strategy(self, key: str, dry_run: bool = False):
        """Set the matrix strategy for the mono-repo

        Args:
            key (str): The key to use for the matrix strategy.
                This also appends the key to the `GITHUB_OUTPUT` environment variable.
            dry_run (bool, optional): Whether to run in dry-run mode. Defaults to False.

        Example:
            $ pymono matrix-strategy python
        """
        projects = find_projects()
        includes = get_includes(projects)
        if not dry_run:
            set_github_output(key, includes)
        return includes


def main() -> None:
    fire.Fire(PyMono)


if __name__ == "__main__":
    main()
