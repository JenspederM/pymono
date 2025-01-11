from uvmono.types import Dependency, Project
from uvmono.github import get_dependents


def test_get_dependents():
    p1 = Project(
        name="project1",
        version="1.0.0",
        path="path1",
        dependencies=[],
    )
    p2 = Project(
        name="project2",
        version="1.0.0",
        path="path2",
        dependencies=[Dependency("project1", is_workspace=True)],
    )
    p3 = Project(
        name="project3",
        version="1.0.0",
        path="path3",
        dependencies=[Dependency("project2", is_workspace=True)],
    )
    projects = [p1, p2, p3]

    dependents = get_dependents(projects)
    assert dependents == {
        "project1": [],
        "project2": [p1],
        "project3": [p2, p1],
    }
