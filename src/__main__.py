"""Main module for running GitRepositoryManager."""

from .git_repository_manager import GitRepositoryManager

if __name__ == "__main__":
    manager = GitRepositoryManager()
    manager.update_all_repositories()
