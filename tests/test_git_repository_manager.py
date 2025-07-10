"""Test module for GitRepositoryManager class."""

import json
import logging
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

from src.git_repository_manager import GitRepositoryManager


class TestGitRepositoryManager(unittest.TestCase):
    """Test cases for GitRepositoryManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_paths_file = Path(self.temp_dir) / "test_paths.json"
        self.manager = GitRepositoryManager(self.temp_paths_file)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init(self):
        """Test GitRepositoryManager initialization."""
        self.assertEqual(self.manager.paths_file, self.temp_paths_file)
        self.assertIsInstance(self.manager.logger, logging.Logger)

    @patch("src.git_repository_manager.GitRepositoryManager.load_paths")
    @patch("src.git_repository_manager.GitRepositoryManager.update_repository")
    def test_update_all_repositories_success(self, mock_update_repo, mock_load_paths):
        """Test successful update of all repositories."""
        mock_load_paths.return_value = {"repo1": "/path/to/repo1", "repo2": "/path/to/repo2"}
        mock_update_repo.return_value = True

        self.manager.update_all_repositories()

        self.assertEqual(mock_update_repo.call_count, 2)
        mock_update_repo.assert_any_call("repo1", "/path/to/repo1")
        mock_update_repo.assert_any_call("repo2", "/path/to/repo2")

    @patch("src.git_repository_manager.GitRepositoryManager.load_paths")
    def test_update_all_repositories_no_paths(self, mock_load_paths):
        """Test update_all_repositories when no paths are found."""
        mock_load_paths.return_value = {}

        with patch.object(self.manager.logger, "warning") as mock_warning:
            self.manager.update_all_repositories()
            mock_warning.assert_called_with("No repository paths found")

    @patch("pathlib.Path.exists")
    def test_update_repository_path_not_exists(self, mock_exists):
        """Test update_repository when path doesn't exist."""
        mock_exists.return_value = False

        with patch.object(self.manager.logger, "error") as mock_error:
            result = self.manager.update_repository("test_repo", "/nonexistent/path")
            self.assertFalse(result)
            mock_error.assert_called_with("Path for test_repo does not exist: /nonexistent/path")

    @patch("pathlib.Path.exists")
    def test_update_repository_not_git_repo(self, mock_exists):
        """Test update_repository when directory is not a git repository."""
        def exists_side_effect(*args, **kwargs):
            if hasattr(exists_side_effect, "call_count"):
                exists_side_effect.call_count += 1
            else:
                exists_side_effect.call_count = 1

            return exists_side_effect.call_count == 1

        mock_exists.side_effect = exists_side_effect

        with patch.object(self.manager.logger, "warning") as mock_warning:
            result = self.manager.update_repository("test_repo", "/some/path")
            self.assertFalse(result)
            mock_warning.assert_called_with("Directory test_repo is not a git repository: /some/path")

    @patch("pathlib.Path.exists")
    @patch("src.git_repository_manager.GitRepositoryManager._has_changes")
    def test_update_repository_no_changes(self, mock_has_changes, mock_exists):
        """Test update_repository when there are no changes."""
        mock_exists.return_value = True
        mock_has_changes.return_value = False

        with patch.object(self.manager.logger, "info") as mock_info:
            result = self.manager.update_repository("test_repo", "/some/path")
            self.assertTrue(result)
            mock_info.assert_called_with("No changes to commit in test_repo: /some/path")

    @patch("pathlib.Path.exists")
    @patch("src.git_repository_manager.GitRepositoryManager._has_changes")
    @patch("src.git_repository_manager.GitRepositoryManager._execute_git_command")
    def test_update_repository_success(self, mock_execute, mock_has_changes, mock_exists):
        """Test successful repository update."""
        mock_exists.return_value = True
        mock_has_changes.return_value = True
        mock_execute.return_value = True

        with patch.object(self.manager.logger, "info") as mock_info:
            result = self.manager.update_repository("test_repo", "/some/path")
            self.assertTrue(result)
            self.assertEqual(mock_execute.call_count, 3)
            mock_info.assert_called_with("Successfully auto-committed and pushed changes in test_repo: /some/path")

    def test_load_paths_file_not_exists(self):
        """Test load_paths when file doesn't exist."""
        with patch.object(self.manager, "_save_paths") as mock_save:
            with patch.object(self.manager.logger, "warning") as mock_warning:
                result = self.manager.load_paths()
                self.assertEqual(result, {})
                mock_save.assert_called_with({})
                mock_warning.assert_called()

    @patch("pathlib.Path.exists")
    def test_load_paths_success(self, mock_exists):
        """Test successful loading of paths."""
        test_paths = {"repo1": "/path/to/repo1", "repo2": "/path/to/repo2"}
        mock_exists.return_value = True

        with patch("builtins.open", mock_open(read_data=json.dumps(test_paths))):
            result = self.manager.load_paths()
            self.assertEqual(result, test_paths)

    @patch("pathlib.Path.exists")
    def test_load_paths_json_decode_error(self, mock_exists):
        """Test load_paths with invalid JSON."""
        mock_exists.return_value = True

        with patch("builtins.open", mock_open(read_data="invalid json")):
            with patch.object(self.manager.logger, "error") as mock_error:
                result = self.manager.load_paths()
                self.assertIsNone(result)
                mock_error.assert_called()

    def test_save_paths_success(self):
        """Test successful saving of paths."""
        test_paths = {"repo1": "/path/to/repo1"}

        with patch("builtins.open", mock_open()) as mock_file:
            self.manager._save_paths(test_paths)
            mock_file.assert_called_once()

    def test_save_paths_error(self):
        """Test _save_paths with OS error."""
        test_paths = {"repo1": "/path/to/repo1"}

        with patch("builtins.open", side_effect=OSError("Permission denied")):
            with patch.object(self.manager.logger, "error") as mock_error:
                self.manager._save_paths(test_paths)
                mock_error.assert_called()

    @patch("subprocess.run")
    def test_has_changes_with_changes(self, mock_run):
        """Test _has_changes when repository has changes."""
        mock_run.return_value = Mock(stdout="M file.txt\n")

        result = self.manager._has_changes(Path("/test/path"))
        self.assertTrue(result)

    @patch("subprocess.run")
    def test_has_changes_no_changes(self, mock_run):
        """Test _has_changes when repository has no changes."""
        mock_run.return_value = Mock(stdout="")

        result = self.manager._has_changes(Path("/test/path"))
        self.assertFalse(result)

    @patch("subprocess.run")
    def test_has_changes_error(self, mock_run):
        """Test _has_changes with subprocess error."""
        mock_run.side_effect = subprocess.CalledProcessError(1, ["git", "status"])

        with patch.object(self.manager.logger, "error") as mock_error:
            result = self.manager._has_changes(Path("/test/path"))
            self.assertIsNone(result)
            mock_error.assert_called()

    @patch("subprocess.run")
    def test_execute_git_command_success(self, mock_run):
        """Test successful git command execution."""
        mock_run.return_value = Mock()

        result = self.manager._execute_git_command(["git", "add", "."], Path("/test/path"))
        self.assertTrue(result)

    @patch("subprocess.run")
    def test_execute_git_command_error(self, mock_run):
        """Test git command execution with error."""
        mock_run.side_effect = subprocess.CalledProcessError(1, ["git", "add"])

        with patch.object(self.manager.logger, "error") as mock_error:
            result = self.manager._execute_git_command(["git", "add", "."], Path("/test/path"))
            self.assertFalse(result)
            mock_error.assert_called()


if __name__ == "__main__":
    unittest.main()
