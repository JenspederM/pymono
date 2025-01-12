from pathlib import Path
import tomllib
from jinja2 import Environment, FileSystemLoader
import mergedeep
import tomli_w

TEMPLATES_DIR = Path(__file__).parent / "templates"


def sync_pyproject(package_dir: Path, package_name: str):
    tomlpath = package_dir / "pyproject.toml"
    template_file = _render("pyproject.toml.j2", package_name=package_name)
    updates = tomllib.loads(template_file)
    with open(tomlpath, "rb") as f:
        current = tomllib.load(f)
    updated = mergedeep.merge(current, updates, strategy=mergedeep.Strategy.REPLACE)
    with open(tomlpath, "wb") as f:
        tomli_w.dump(updated, f)


def add_project_standards(package_dir: Path):
    package_name = package_dir.name.replace("-", "_")
    _create_tests(package_dir / "tests", package_name)
    _add_pyproject_defaults(package_dir, package_name)


def create_filter(project_path: Path, dependents: list[Path]) -> str:
    deps = [(p.path / "**").as_posix() for p in dependents]
    if not deps:
        return _render("filter.yml.j2", path=project_path.as_posix())
    return _render("filter.yml.j2", path=project_path.as_posix(), dependencies=deps)


def _render(template_name: str, **kwargs) -> str:
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


def create_dockerfile(
    ubuntu_version: str,
    spark_version: str,
    uv_version: str,
):
    return _render(
        "Dockerfile.j2",
        ubuntu_version=ubuntu_version,
        spark_version=spark_version,
        uv_version=uv_version,
    )


def create_devcontainer(
    package_name: str,
    dockerfile_path: Path,
):
    return _render(
        "devcontainer.json.j2",
        package_name=package_name,
        docker_compose_file=dockerfile_path,
    )


def _create_tests(tests_dir: Path, package_name: str):
    main_template = _render("tests_init.py.j2", package_name=package_name)
    conftest_template = _render("conftest.py.j2", package_name=package_name)
    tests_dir.mkdir()
    (tests_dir / "__init__.py").write_text("")
    (tests_dir / "test_main.py").write_text(f"{main_template}\n")
    (tests_dir / "conftest.py").write_text(f"{conftest_template}\n")


def _add_pyproject_defaults(package_dir: Path, package_name: str):
    init_template = _render("package_init.py.j2", package_name=package_name)
    init_template_path = package_dir / "src" / package_name / "__init__.py"
    init_template_path.write_text(f"{init_template}\n")
    with open(package_dir / "pyproject.toml", "a") as fh:
        pyproject_template = _render("pyproject.toml.j2", package_name=package_name)
        fh.write(pyproject_template)
