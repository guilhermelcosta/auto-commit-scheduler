"""Constants and configuration values for the auto-commit scheduler."""

from datetime import datetime
from pathlib import Path

JSON_FILE = Path("files/repositories.json")
LOG_FILE = Path("files/git_manager.log")
DEFAULT_COMMIT_MESSAGE = f"Auto-commit: Updated files - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
READ_COMMAND = "r"
WRITE_COMMAND = "w"
