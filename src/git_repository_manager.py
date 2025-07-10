"""Git Repository Manager module.

This module provides functionality for managing Git operations across multiple repositories.
It includes the GitRepositoryManager class which can automatically commit and push changes
to repositories defined in a JSON configuration file.
"""

import json
import logging
import subprocess
from pathlib import Path

from .constants import DEFAULT_COMMIT_MESSAGE, JSON_FILE, LOG_FILE, READ_COMMAND, WRITE_COMMAND


class GitRepositoryManager:
    """Manages Git operations for multiple repositories."""

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()],
    )

    def __init__(self, paths_file: Path = JSON_FILE):
        """Initialize GitRepositoryManager with a paths file.

        Args:
            paths_file: Path to JSON file containing repository paths.

        """
        self.paths_file = paths_file
        self.logger = logging.getLogger(__name__)

    def update_all_repositories(self) -> None:
        """Update all repositories defined in the paths file."""
        paths = self.load_paths()

        if not paths:
            self.logger.warning("No repository paths found")
            return

        success_count = 0

        for name, path in paths.items():
            if self.update_repository(name, path):
                success_count += 1

        self.logger.info(f"Successfully updated {success_count}/{len(paths)} repositories")

    def update_repository(self, name: str, path: str) -> bool:
        """Update a single repository with auto-commit and push."""
        repo_path = Path(path)

        if not repo_path.exists():
            self.logger.error(f"Path for {name} does not exist: {path}")
            return False

        if not (repo_path / ".git").exists():
            self.logger.warning(f"Directory {name} is not a git repository: {path}")
            return False

        try:
            if not self._has_changes(repo_path):
                self.logger.info(f"No changes to commit in {name}: {path}")
                return True

            if not self._execute_git_command(["git", "add", "."], repo_path):
                return False

            if not self._execute_git_command(["git", "commit", "-m", DEFAULT_COMMIT_MESSAGE], repo_path):
                return False

            if not self._execute_git_command(["git", "push"], repo_path):
                return False

            self.logger.info(f"Successfully auto-committed and pushed changes in {name}: {path}")
            return True

        except Exception as e:
            self.logger.error(f"Unexpected error updating {name}: {path} - {e}")
            return False

    def load_paths(self) -> dict[str, str] | None:
        """Load repository paths from JSON file."""
        if not self.paths_file.exists():
            self.logger.warning(f"{self.paths_file} not found. Creating empty paths file.")
            self._save_paths({})
            return {}

        try:
            with open(self.paths_file, READ_COMMAND) as file:
                paths = json.load(file)
                return paths
        except json.JSONDecodeError as e:
            self.logger.error(f"Error reading {self.paths_file}: {e}")

    def _save_paths(self, paths: dict[str, str]) -> None:
        """Save paths to JSON file."""
        try:
            with open(self.paths_file, WRITE_COMMAND) as file:
                json.dump(paths, file, indent=4)
        except OSError as e:
            self.logger.error(f"Error writing to {self.paths_file}: {e}")

    def _has_changes(self, repo_path: Path) -> bool | None:
        """Check if repository has uncommitted changes."""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"], cwd=repo_path, capture_output=True, text=True, check=True
            )
            return bool(result.stdout.strip())
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to check git status in {repo_path}: {e}")

    def _execute_git_command(self, command: list[str], repo_path: Path) -> bool:
        """Execute a git command in the specified repository."""
        try:
            subprocess.run(command, cwd=repo_path, check=True, capture_output=True, text=True)
            return True
        except subprocess.CalledProcessError as e:
            error_msg = f"Git command {' '.join(command)} failed in {repo_path}: {e}"
            if e.stdout:
                error_msg += f"\nSTDOUT: {e.stdout.strip()}"
            if e.stderr:
                error_msg += f"\nSTDERR: {e.stderr.strip()}"
            self.logger.error(error_msg)
            return False
