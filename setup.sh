#!/bin/bash

PROJECT_PATH="$(cd "$(dirname "$0")" && pwd)"

mkdir -p "$PROJECT_PATH/files"

chmod +x "$PROJECT_PATH/run_git_manager.sh"

CRON_ENTRY="@reboot sleep 60 && $PROJECT_PATH/run_git_manager.sh"

(crontab -l 2>/dev/null | grep -Fxq "$CRON_ENTRY") || (
    (crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -
    echo "Crontab entry added: $CRON_ENTRY"
)

echo "Setup completed. The Git Repository Manager will run on system reboot."
echo "To test manually, run: python3 -m src"
