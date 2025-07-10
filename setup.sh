#!/bin/bash

SCRIPT_PATH="$(pwd)/script.py"

CRON_ENTRY="@reboot /usr/bin/python3 $SCRIPT_PATH"

(crontab -l 2>/dev/null | grep -Fxq "$CRON_ENTRY") || (
    (crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -
    echo "Crontab entry added."
)
