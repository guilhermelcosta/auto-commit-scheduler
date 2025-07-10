"""Constants and configuration values for the auto-commit scheduler."""

from datetime import datetime
from pathlib import Path

_CURRENT_DIR = Path(__file__).parent
_FILES_DIR = _CURRENT_DIR.parent / "files"
JSON_FILE = _FILES_DIR / "repositories.json"
LOG_FILE = _FILES_DIR / "git_manager.log"
DEFAULT_COMMIT_MESSAGE = f"Auto-commit: Updated files - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
READ_COMMAND = "r"
WRITE_COMMAND = "w"
