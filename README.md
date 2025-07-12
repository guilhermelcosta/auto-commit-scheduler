# Auto-Commit Scheduler

A Python-based tool that automatically commits and pushes changes to multiple Git repositories. This tool is designed to run on a schedule and manage your Git repositories automatically with robust network handling and SSH authentication.

## Overview

The Auto-Commit Scheduler monitors multiple Git repositories and automatically commits and pushes any changes it finds. It's particularly useful for:

- Automatically backing up configuration files
- Keeping documentation repositories up to date
- Synchronizing development environments
- Maintaining version control for frequently updated projects

## Features

- **Automatic Git Operations**: Automatically adds, commits, and pushes changes
- **Multi-Repository Support**: Manages multiple repositories from a single configuration
- **Comprehensive Logging**: Detailed logging of all operations with timestamps
- **Flexible Scheduling**: Runs on a schedule via cron (e.g., every 3 hours by default).
- **Network-Aware**: Waits for network connectivity before attempting operations
- **SSH Authentication**: Automatically handles SSH agent and key management
- **Error Handling**: Robust error handling and reporting
- **Status Checking**: Only commits when changes are detected
- **Fully Tested**: Comprehensive unit test suite

## Project Structure

```
auto-commit-scheduler/
├── README.md                          # This documentation
├── setup.sh                           # Main installation script
├── run_git_manager.sh                 # Production execution script with network handling
├── src/                               # Python package source code
│   ├── __init__.py                    # Package initialization
│   ├── __main__.py                    # Module entry point (python -m src)
│   ├── constants.py                   # Configuration constants
│   └── git_repository_manager.py      # Core Git operations manager
├── tests/                             # Test files
│   ├── __init__.py                    # Test package initialization
│   └── test_git_repository_manager.py # Unit tests
└── files/                             # Data and log files
    ├── repositories.json              # Repository configuration
    ├── git_manager.log                # Application logs
    └── cron.log                       # Cron execution logs
```

## How It Works

1. **Configuration**: Repository paths are stored in `files/repositories.json`
2. **Network Check**: The system waits for network connectivity before proceeding
3. **SSH Setup**: Automatically configures SSH agent and loads SSH keys
4. **Detection**: The system checks each repository for uncommitted changes
5. **Auto-commit**: If changes are found, they are automatically staged, committed, and pushed
6. **Logging**: All operations are logged to both `files/git_manager.log` and `files/cron.log`
7. **Scheduling**: Runs automatically on a schedule via cron.

## Installation and Setup

### Prerequisites

- Python 3.10 or higher
- Git installed and configured
- SSH keys set up for your repositories (`~/.ssh/id_rsa` or `~/.ssh/id_ed25519`)
- Linux/Unix system with cron support
- Network connectivity for Git operations

### Quick Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/guilhermelcosta/auto-commit-scheduler
   cd auto-commit-scheduler
   ```

2. **Configure your repositories**:
   Edit `files/repositories.json` to include your repositories:
   ```json
   {
       "my_project": "/path/to/your/project",
       "documentation": "/home/user/docs",
       "config_files": "/home/user/.config"
   }
   ```

3. **Run the setup script**:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

### What the setup.sh script does

The `setup.sh` script automatically:

- Creates the `files/` directory if it doesn't exist
- Makes the `run_git_manager.sh` script executable
- Adds a cron job that runs the auto-commit script every 3 hours.
- Uses the `0 */3 * * *` cron expression.
- Checks if the cron entry already exists to avoid duplicates
- Provides feedback when the cron job is successfully added

**Cron entry added**: `0 */3 * * * /full/path/to/run_git_manager.sh`

## Configuration

### Repository Configuration

Edit `files/repositories.json` to specify which repositories to monitor:

```json
{
    "repository_name": "/absolute/path/to/repository",
    "another_repo": "/home/user/projects/another-repo",
    "config_backup": "/home/user/.config"
}
```

**Requirements**:
- Use absolute paths for all repositories
- Each repository must be a valid Git repository (contains `.git` folder)
- You must have push permissions to the remote repositories
- SSH keys must be properly configured for authentication

### Commit Message

The default commit message format is: `Auto-commit: Updated files - YYYY-MM-DD HH:MM`

You can modify this in `src/constants.py`:

```python
DEFAULT_COMMIT_MESSAGE = f"Your custom message - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
```

## Usage

### Manual Execution

To run the auto-commit process manually:

```bash
# Using the Python module (recommended)
python3 -m src

# Using the production script (with network checks)
./run_git_manager.sh
```

### Automatic Execution

After running `setup.sh`, the script will automatically execute every 3 hours. You can also manually manage the cron job:

```bash
# View current cron jobs
crontab -l

# Edit cron jobs manually
crontab -e

# Remove the auto-commit cron job
crontab -l | grep -v "run_git_manager.sh" | crontab -
```

## Logging

The system provides comprehensive logging:

### Application Logs (`files/git_manager.log`)
- Repository processing status
- Git command execution results
- Error messages and warnings
- Success/failure counts

### Cron Logs (`files/cron.log`)
- Network connectivity checks
- SSH agent setup
- Execution timestamps
- Exit codes

**Log format**: `YYYY-MM-DD HH:MM:SS - LEVEL - Message`

## Safety Features

- **Network Awareness**: Waits up to 5 minutes for network connectivity before proceeding
- **SSH Authentication**: Automatically manages SSH agent and key loading
- **Change Detection**: Only commits when actual changes are detected
- **Repository Validation**: Verifies paths exist and contain Git repositories
- **Error Isolation**: Continues processing other repositories if one fails
- **Detailed Logging**: Comprehensive logging for troubleshooting
- **Non-destructive**: Only adds, commits, and pushes (no destructive operations)
- **Graceful Failures**: Proper error handling and exit codes

## Production Features

The `run_git_manager.sh` script includes production-ready features:

- **Network Monitoring**: Pings Google DNS (8.8.8.8) to verify connectivity
- **SSH Agent Management**: Automatically starts and configures SSH agent
- **Environment Variables**: Preserves necessary environment variables
- **Comprehensive Logging**: All operations logged with timestamps
- **Error Recovery**: Graceful handling of network and authentication failures

## Testing

The project includes comprehensive unit tests. To run them:

```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run specific test file
pytest tests/test_git_repository_manager.py

# Check test coverage
pytest --cov=src
```

**Test Coverage**: 17 tests covering all major functionality including error conditions.

## Troubleshooting

### Common Issues

1. **Network Errors**: Check `files/cron.log` for network connectivity issues
2. **SSH Authentication**: Ensure SSH keys are properly configured and loaded
3. **Permission Denied**: Verify you have write permissions and SSH keys are set up
4. **Repository Not Found**: Check paths in `repositories.json` are correct and absolute
5. **Cron Not Running**: Check if the cron service is running: `systemctl status cron`

### Log Files

```bash
# Check application logs
tail -f files/git_manager.log

# Check cron execution logs
tail -f files/cron.log

# Check system cron logs
sudo tail -f /var/log/cron
```

### Manual Testing

```bash
# Test the Python module
python3 -m src

# Test configuration loading
python3 -c "from src.git_repository_manager import GitRepositoryManager; mgr = GitRepositoryManager(); print(mgr.load_paths())"

# Test network connectivity (from run_git_manager.sh)
ping -c 1 8.8.8.8
```

## Technical Details

### Import System
The project uses relative imports within the `src` package for clean module organization:
- `from .constants import ...` - imports from the same package
- Executed via `python -m src` to leverage Python's module system

### Path Resolution
File paths in `constants.py` are resolved relative to the constants file location using `Path(__file__).parent`, ensuring they work correctly regardless of the working directory.

### Architecture
- **Modular Design**: Clean separation between configuration, logging, and Git operations
- **Error Handling**: Comprehensive exception handling with detailed logging
- **Production Ready**: Network awareness, SSH management, and robust cron integration

## Customization

You can extend the functionality by modifying:

- `src/constants.py`: Change file paths, commit messages, or add new constants
- `src/git_repository_manager.py`: Modify Git operations or add new features
- `run_git_manager.sh`: Modify network checks, SSH handling, or logging
- `setup.sh`: Change cron scheduling or installation behavior

### Cron Scheduling

By default, the `setup.sh` script configures the cron job to run every 3 hours (`0 */3 * * *`). You can customize this schedule by editing the `CRON_ENTRY` variable in the `setup.sh` script before running it.

Here are some common cron schedule examples:

- **Every hour**: `0 * * * *`
- **Every 6 hours**: `0 */6 * * *`
- **Once a day at midnight**: `0 0 * * *`
- **On system reboot**: `@reboot`

To apply a new schedule, modify the `setup.sh` script and run it again. The script will add the new cron job without creating duplicates.

## Security Considerations

- Ensure your Git repositories use SSH keys or secure authentication
- Review the repositories list regularly to avoid accidentally committing sensitive data
- Monitor the log files for any suspicious activity
- Consider running the script with limited user permissions
- SSH keys are loaded automatically but never stored in logs

## Requirements

See `requirements.txt` for Python dependencies. The system has minimal external dependencies and uses primarily Python standard library modules.

## Contributing

Contributions are welcome! Please:

- Add docstrings to all functions and classes
- Include unit tests for new features
- Update documentation when adding new functionality
- Follow the existing code style and patterns
