#!/bin/bash

# Auto-sync script for local development
# This script can be run locally or via cron to sync changes

set -e

# Configuration
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_FILE="$REPO_DIR/.taskmaster/logs/auto-sync.log"
MAX_LOG_SIZE=1048576  # 1MB

# Create logs directory if it doesn't exist
mkdir -p "$(dirname "$LOG_FILE")"

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to rotate log if it gets too large
rotate_log() {
    if [ -f "$LOG_FILE" ] && [ $(stat -f%z "$LOG_FILE" 2>/dev/null || stat -c%s "$LOG_FILE" 2>/dev/null || echo 0) -gt $MAX_LOG_SIZE ]; then
        mv "$LOG_FILE" "${LOG_FILE}.old"
        log "Log rotated due to size limit"
    fi
}

# Function to check if we're in a git repository
check_git_repo() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log "ERROR: Not in a git repository"
        exit 1
    fi
}

# Function to check for changes
check_changes() {
    if [ -n "$(git status --porcelain)" ]; then
        log "Changes detected:"
        git status --porcelain | while read line; do
            log "  $line"
        done
        return 0
    else
        log "No changes detected"
        return 1
    fi
}

# Function to commit and push changes
sync_changes() {
    log "Starting sync process..."
    
    # Add all changes
    git add .
    
    # Create commit with timestamp
    TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M:%S UTC")
    COMMIT_MSG="chore: Auto-sync changes at $TIMESTAMP

Automated sync of repository changes detected by local auto-sync script."
    
    git commit -m "$COMMIT_MSG"
    log "Created commit: $COMMIT_MSG"
    
    # Push changes
    git push origin main
    log "Pushed changes to origin/main"
    
    # Check if we should create a tag
    CHANGES_COUNT=$(git diff --stat HEAD~1 | grep -o '[0-9]* files changed' | grep -o '[0-9]*' || echo "0")
    log "Changes count: $CHANGES_COUNT files"
    
    if [ "$CHANGES_COUNT" -gt 3 ]; then
        # Create patch version tag for significant changes
        LATEST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
        VERSION=$(echo $LATEST_TAG | sed 's/v//')
        MAJOR=$(echo $VERSION | cut -d. -f1)
        MINOR=$(echo $VERSION | cut -d. -f2)
        PATCH=$(echo $VERSION | cut -d. -f3)
        NEW_PATCH=$((PATCH + 1))
        NEW_TAG="v${MAJOR}.${MINOR}.${NEW_PATCH}"
        
        git tag -a "$NEW_TAG" -m "Auto-release: Significant changes detected ($CHANGES_COUNT files)"
        git push origin "$NEW_TAG"
        log "Created and pushed tag: $NEW_TAG"
    fi
}

# Function to setup cron job
setup_cron() {
    CRON_SCRIPT="$REPO_DIR/scripts/auto-sync.sh"
    CRON_JOB="0 * * * * cd $REPO_DIR && $CRON_SCRIPT >> $LOG_FILE 2>&1"
    
    # Check if cron job already exists
    if crontab -l 2>/dev/null | grep -q "$CRON_SCRIPT"; then
        log "Cron job already exists"
    else
        # Add cron job
        (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
        log "Cron job added: $CRON_JOB"
    fi
}

# Function to remove cron job
remove_cron() {
    CRON_SCRIPT="$REPO_DIR/scripts/auto-sync.sh"
    crontab -l 2>/dev/null | grep -v "$CRON_SCRIPT" | crontab -
    log "Cron job removed"
}

# Main execution
main() {
    rotate_log
    log "=== Auto-sync started ==="
    
    # Change to repository directory
    cd "$REPO_DIR"
    
    # Check if we're in a git repository
    check_git_repo
    
    # Check for changes
    if check_changes; then
        sync_changes
        log "Sync completed successfully"
    else
        log "No sync needed"
    fi
    
    log "=== Auto-sync finished ==="
}

# Handle command line arguments
case "${1:-}" in
    "setup-cron")
        setup_cron
        ;;
    "remove-cron")
        remove_cron
        ;;
    "status")
        log "Checking cron status..."
        if crontab -l 2>/dev/null | grep -q "auto-sync.sh"; then
            log "Cron job is active"
            crontab -l | grep "auto-sync.sh"
        else
            log "No cron job found"
        fi
        ;;
    *)
        main
        ;;
esac
