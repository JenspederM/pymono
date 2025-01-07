import json
import os
from pathlib import Path
import tomllib
from typing import Any

from pymono.types import Dependency, Project


def find_projects(root="."):
    projects = {}
    for toml in Path(root).rglob("pyproject.toml"):
        with open(toml, "rb") as fh:
            data = tomllib.load(fh)

        project = data.get("project")
        if not project:
            raise ValueError(f"Missing project in {toml}")

        name = project.get("name")
        version = project.get("version")
        if not name or not version:
            raise ValueError(
                f"Missing name or version in {toml}"
                " | "
                f"name={name}, version={version}"
            )

        project_dependencies = project.get("dependencies", [])
        uv_sources = data.get("tool", {}).get("uv", {}).get("sources", {})
        dependencies = []
        for dep in project_dependencies:
            dependencies.append(Dependency(dep, dep in uv_sources))
        projects[name] = Project(name, version, toml.parent, dependencies)

    return projects


def get_includes(projects: dict[str, Project]):
    includes = []
    dependents = get_dependents(list(projects.values()))
    for project in projects.values():
        includes.append(
            {
                "path": project.path.as_posix(),
                "name": project.name,
                "dependents": [
                    (p.path / "**").as_posix() for p in dependents.get(project.name, [])
                ],
            }
        )

    return includes


def set_github_output(key: str, value: Any):
    include_statement = json.dumps({key: value})
    msg = f"matrix={include_statement}"
    print(f"Set GITHUB_OUTPUT to:\n{msg}")
    try:
        with open(os.environ["GITHUB_OUTPUT"], "a") as fh:
            print(msg, file=fh)
    except KeyError:
        raise RuntimeError("GITHUB_OUTPUT environment variable not set")


def _get_dependents(project: Project, projects: list[Project]):
    dependents = []
    for other in projects:
        if project.name == other.name:
            continue
        if any(project.name == dep.name for dep in other.dependencies):
            dependents.append(other)
            dependents.extend(_get_dependents(other, projects))
    return dependents


def get_dependents(projects: list[Project]):
    dependents: dict[str, list[Project]] = {project.name: [] for project in projects}
    for project in projects:
        dependents[project.name] = _get_dependents(project, projects)
    return dependents