#!/bin/bash

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_FILE="$PROJECT_DIR/files/cron.log"

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

wait_for_network() {
    local max_attempts=30
    local attempt=0

    log_message "Waiting for network connection..."

    while [ $attempt -lt $max_attempts ]; do
        if ping -c 1 8.8.8.8 >/dev/null 2>&1; then
            log_message "Network connection established"
            return 0
        fi

        attempt=$((attempt + 1))
        log_message "Network attempt $attempt/$max_attempts failed, waiting 10 seconds..."
        sleep 10
    done

    log_message "ERROR: Network connection not available after $max_attempts attempts"
    return 1
}

log_message "Starting Git Repository Manager..."

if ! wait_for_network; then
    log_message "Exiting due to network unavailability"
    exit 1
fi

export SSH_AUTH_SOCK="$SSH_AUTH_SOCK"
export HOME="$HOME"

if ! pgrep -u "$USER" ssh-agent > /dev/null; then
    log_message "SSH agent not running, starting..."
    eval "$(ssh-agent -s)" >> "$LOG_FILE" 2>&1
fi

if [ -f "$HOME/.ssh/id_rsa" ]; then
    ssh-add "$HOME/.ssh/id_rsa" >> "$LOG_FILE" 2>&1
elif [ -f "$HOME/.ssh/id_ed25519" ]; then
    ssh-add "$HOME/.ssh/id_ed25519" >> "$LOG_FILE" 2>&1
fi

cd "$PROJECT_DIR" || {
    log_message "ERROR: Could not change to project directory"
    exit 1
}

log_message "Running Git Repository Manager..."
python3 -m src >> "$LOG_FILE" 2>&1
log_message "Git Repository Manager finished with exit code: $?"
