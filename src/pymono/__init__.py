import json
import os
from pathlib import Path
import shutil
import subprocess
import fire
from jinja2 import Environment, FileSystemLoader

TEMPLATES_DIR = Path(__file__).parent / "templates"


def render_template(template_name: str, **kwargs) -> str:
    """Render a jinja2 template

    Args:
        template_name (str): The name of the template to render
        **kwargs: Keyword arguments to pass to the template

    Returns:
        str: The rendered template
    """
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    template = env.get_template(template_name)
    return template.render(**kwargs)


class PyMono:
    """PyMono is a tool to help manage mono-repos in python"""

    def __init__(self):
        self._root = find_git_root()
        self._packages_root = self._root / "packages"
        self._packages = [p for p in self._packages_root.iterdir() if p.is_dir()]

    def _create_tests(self, tests_dir: Path, package_name: str):
        main_template = render_template("tests_init.py.j2", package_name=package_name)
        tests_dir.mkdir()
        (tests_dir / "__init__.py").write_text("")
        (tests_dir / "test_main.py").write_text(main_template)
        (tests_dir / "conftest.py").write_text("import pytest")

    def _add_pyproject_defaults(self, package_dir: Path):
        package_name = package_dir.name.replace("-", "_")
        init_template = render_template("package_init.py.j2", package_name=package_name)
        template = render_template("pyproject.toml.j2", package_name=package_name)
        (package_dir / "src" / package_name / "__init__.py").write_text(init_template)
        with open(package_dir / "pyproject.toml", "a") as fh:
            fh.write(template)

    def new(self, package_name: str):
        """Create a new package in the mono-repo.

        Args:
            package_name (str): The name of the package to create.
        """
        self._has_uv()
        package_dir = self._packages_root / package_name
        if package_dir.exists():
            raise FileExistsError(f"Package {package_name} already exists")
        package_dir.mkdir()
        subprocess.run(["uv", "init", "--package", "--directory", str(package_dir)])
        self._create_tests(package_dir / "tests", package_name.replace("-", "_"))
        self._add_pyproject_defaults(package_dir)
        subprocess.run(
            [
                "uv",
                "add",
                "pytest",
                "pytest-cov",
                "--dev",
                "--directory",
                str(package_dir),
            ]
        )

        assert (
            package_dir / "pyproject.toml"
        ).exists(), f"Failed to create package: {package_name}"

    def list(self):
        """List the packages in the mono-repo"""
        packages = self._root / "packages"
        packages = [p.name for p in packages.iterdir() if p.is_dir()]
        return sorted(packages)

    def _has_uv(self):
        """Check if `uv` is installed"""
        has_uv = shutil.which("uv")
        if not has_uv:
            msg = """`uv` not found.

            This package requires the `uv` command line tool.

            You can find information on how to install it here:
                https://docs.astral.sh/uv/getting-started/installation/ 
            """
            raise RuntimeError(msg)
        return True

    def _get_relative_package_path(self, package_name: str):
        """Get the path to the package"""
        package_path = self._packages_root / package_name
        if not package_path.exists():
            raise FileNotFoundError(f"Package {package_name} not found")
        return package_path.relative_to(self._packages_root.parent).as_posix()

    def matrix_strategy(self, key: str):
        """Set the matrix strategy for the mono-repo

        Args:
            key (str): The key to use for the matrix strategy.
                This also appends the key to the `GITHUB_OUTPUT` environment variable.

        Example:
            $ pymono matrix-strategy python
        """
        if (self._packages_root / "shared").exists():
            shared_package_path = self._get_relative_package_path("shared")
        else:
            shared_package_path = None

        included_packages = []
        for package in self._packages:
            included_packages.append(
                {
                    "path": self._get_relative_package_path(package.stem),
                    "name": package.stem,
                    "shared": shared_package_path,
                }
            )

        include_statement = json.dumps({key: included_packages})
        msg = f"matrix={include_statement}"
        print(f"Set GITHUB_OUTPUT to:\n{msg}")
        try:
            with open(os.environ["GITHUB_OUTPUT"], "a") as fh:
                print(msg, file=fh)
        except KeyError:
            raise RuntimeError("GITHUB_OUTPUT environment variable not set")
        return included_packages


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


def main() -> None:
    fire.Fire(PyMono)


if __name__ == "__main__":
    main()
