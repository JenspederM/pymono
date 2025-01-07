from dataclasses import dataclass
from pathlib import Path


@dataclass
class Dependency:
    name: str
    is_workspace: bool


@dataclass
class Project:
    name: str
    version: str
    path: Path
    dependencies: list[Dependency]


@dataclass
class Include:
    path: str
    name: str
    dependencies: list[str]
