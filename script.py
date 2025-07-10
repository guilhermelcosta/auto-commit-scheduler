"""Auto-commit scheduler script.

This module provides the main entry point for automatically updating
Git repositories using the GitRepositoryManager.
"""
from git_repository_manager import GitRepositoryManager


def main():
    """Run the main function."""
    manager = GitRepositoryManager()
    manager.update_all_repositories()

if __name__ == "__main__":
    main()
