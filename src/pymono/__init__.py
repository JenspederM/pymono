from __future__ import annotations
import subprocess
import fire

from pymono.github import find_projects, get_includes, set_github_output
from pymono.template import add_pyproject_defaults, create_devcontainer, create_tests
from pymono.utils import find_git_root, has_uv


class PyMono:
    """PyMono: Manage Python mono-repos effortlessly.

    Commands:
        - `new`: Create a new package in the mono-repo.
        - `list`: List the packages in the mono-repo.
        - `add-devcontainer`: Add a devcontainer configuration to a package.
        - `matrix-strategy`: Set the matrix strategy for the mono-repo.

    Example usage:
        $ pymono new mypackage
        $ pymono list
        $ pymono add-devcontainer mypackage
    """

    def __init__(self):
        self._root = find_git_root()
        self._packages_root = self._root / "packages"
        self._packages = [
            p
            for p in self._packages_root.iterdir()
            if p.is_dir() and (p / "pyproject.toml").exists()
        ]

    def list(self):
        """List the packages in the mono-repo"""
        packages = [p.name for p in self._packages_root.iterdir() if p.is_dir()]
        return sorted(packages)

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
        package_name = package_dir.name.replace("-", "_")
        create_tests(package_dir / "tests", package_name)
        add_pyproject_defaults(package_dir, package_name)
        subprocess.run(["uv", "add", *default_packages, "--dev", *dir_cmd])

    def add_devcontainer(
        self,
        package_name: str = "",
        all: bool = False,
        dry_run: bool = False,
        ubuntu_version: str = "22.04",
        spark_version: str = "3.5.4",
        uv_version: str = "0.5.15",
    ):
        """Add a devcontainer configuration to a package

        Args:
            package_name (str): The name of the package to add the devcontainer to.
            all (bool, optional): Whether to add the devcontainer to all packages.
            dry_run (bool, optional): Whether to run in dry-run mode.
            ubuntu_version (str, optional): The version of ubuntu to use.
            spark_version (str, optional): The version of spark to use.
            uv_version (str, optional): The version of uv to use.
        """
        if not package_name and not all:
            return "Either `package_name` or `all` must be set. Use `--help` for more information."

        packages = self.list() if all else [package_name]
        print(f"Adding devcontainer configuration to {', '.join(packages)}")
        for package in packages:
            package_dir = (self._packages_root / package).relative_to(self._root)
            dot_to_root = [".." for _ in package_dir.as_posix().split("/")]
            dockerfile = f'{"/".join(dot_to_root)}/Dockerfile'
            template = create_devcontainer(
                package,
                dockerfile,
                f"ubuntu-{ubuntu_version}",
                spark_version,
                uv_version,
            )
            if dry_run:
                print(f"[DRY_RUN] Creating devcontainer configuration for {package}")
                continue
            print(f"Creating devcontainer configuration for {package}")
            path = self._root / package_dir / ".devcontainer" / "devcontainer.json"
            path.parent.mkdir(exist_ok=True)
            with open(path, "w") as f:
                f.write(template)
            print(f"Successfully created devcontainer configuration for {package}")
        if dry_run:
            return f"[DRY_RUN] Successfully created devcontainer configuration{''if all else 's'}"
        return f"Successfully created devcontainer configuration{''if all else 's'}"

    def _get_relative_package_path(self, package_name: str):
        """Get the path to the package"""
        package_path = self._packages_root / package_name
        if not package_path.exists():
            raise FileNotFoundError(f"Package {package_name} not found")
        return package_path.relative_to(self._packages_root.parent).as_posix()

    def matrix_strategy(self, key: str, dry_run: bool = False) -> list:
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
