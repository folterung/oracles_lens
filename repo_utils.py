from pathlib import Path
from typing import Protocol
from git import Repo


class Committer(Protocol):
    """Abstraction for committing files."""

    def add_and_commit(self, path: Path, message: str) -> None:
        ...


class GitCommitter:
    """Commit files using GitPython."""

    def __init__(self, repo_path: Path):
        self.repo = Repo(repo_path)

    def add_and_commit(self, path: Path, message: str) -> None:
        self.repo.git.add(str(path))
        self.repo.index.commit(message)
