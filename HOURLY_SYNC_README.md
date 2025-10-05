# 🔄 Hourly Auto-Sync Setup

This repository now includes automated hourly synchronization to ensure all changes are automatically committed and pushed to GitHub.

## 🚀 Features

### GitHub Actions (Cloud-based)
- **Schedule**: Runs every hour at minute 0
- **Automatic**: Detects changes and commits them
- **Smart Tagging**: Creates version tags for significant changes
- **Reporting**: Generates sync reports for each run

### Local Cron Job (Local machine)
- **Schedule**: Runs every hour on your local machine
- **Logging**: Detailed logs in `.taskmaster/logs/auto-sync.log`
- **Smart Detection**: Only commits when changes are detected
- **Version Management**: Auto-creates tags for significant updates

## 📋 Setup Instructions

### Quick Setup (Recommended)
```bash
# Run the automated setup script
./scripts/setup-hourly-sync.sh setup
```

### Manual Setup Options

#### 1. GitHub Actions Only
```bash
./scripts/setup-hourly-sync.sh github
```

#### 2. Local Cron Only
```bash
./scripts/setup-hourly-sync.sh local
```

#### 3. Test Current Setup
```bash
./scripts/setup-hourly-sync.sh test
```

#### 4. Check Status
```bash
./scripts/setup-hourly-sync.sh status
```

## 🛠️ How It Works

### GitHub Actions Workflow
- **File**: `.github/workflows/hourly-sync.yml`
- **Trigger**: Every hour (`0 * * * *`)
- **Process**:
  1. Checks for uncommitted changes
  2. Commits changes with timestamp
  3. Pushes to main branch
  4. Creates tags for significant changes (>5 files)
  5. Generates sync reports

### Local Auto-Sync Script
- **File**: `scripts/auto-sync.sh`
- **Schedule**: Cron job every hour
- **Process**:
  1. Checks for changes in repository
  2. Commits with descriptive messages
  3. Pushes to GitHub
  4. Creates version tags for significant changes (>3 files)
  5. Logs all activities

## 📊 Monitoring

### Check Status
```bash
# View current setup status
./scripts/setup-hourly-sync.sh status

# Check cron job
./scripts/auto-sync.sh status

# View recent logs
tail -f .taskmaster/logs/auto-sync.log
```

### GitHub Actions
- View runs: `https://github.com/[owner]/[repo]/actions`
- Look for "Hourly Repository Sync" workflow
- Check artifacts for sync reports

## 🔧 Configuration

### Cron Schedule
The default schedule is every hour (`0 * * * *`). To modify:

1. Remove current cron: `./scripts/auto-sync.sh remove-cron`
2. Edit `scripts/auto-sync.sh` line with cron schedule
3. Re-run setup: `./scripts/setup-hourly-sync.sh local`

### Change Detection Thresholds
- **GitHub Actions**: Creates tags for >5 file changes
- **Local Script**: Creates tags for >3 file changes
- **Both**: Only commit when actual changes detected

### Log Management
- Logs are automatically rotated when they exceed 1MB
- Old logs are saved as `.old` files
- Logs are stored in `.taskmaster/logs/`

## 🚨 Troubleshooting

### Common Issues

#### 1. GitHub Actions Not Running
```bash
# Check if workflow file exists
ls -la .github/workflows/hourly-sync.yml

# Verify GitHub CLI authentication
gh auth status

# Check repository permissions
gh repo view
```

#### 2. Local Cron Not Working
```bash
# Check if cron job exists
crontab -l | grep auto-sync

# Test script manually
./scripts/auto-sync.sh

# Check logs
tail -f .taskmaster/logs/auto-sync.log
```

#### 3. Authentication Issues
```bash
# For GitHub Actions: Ensure GITHUB_TOKEN has proper permissions
# For local: Ensure git credentials are configured
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Manual Override
If you need to manually sync:
```bash
# Run auto-sync manually
./scripts/auto-sync.sh

# Or use standard git commands
git add .
git commit -m "Manual sync"
git push origin main
```

## 📈 Benefits

1. **Never Lose Changes**: All modifications are automatically saved
2. **Version History**: Automatic tagging creates clear version history
3. **Backup**: Changes are immediately backed up to GitHub
4. **Collaboration**: Team members always have the latest changes
5. **Audit Trail**: Detailed logs of all sync activities

## 🔄 Workflow Integration

This auto-sync works alongside:
- Manual commits and pushes
- GitHub Actions workflows
- Pull request processes
- Release management

The system is designed to be non-intrusive and only commits when actual changes are detected.

## 📝 Logs and Reports

### Local Logs
- **Location**: `.taskmaster/logs/auto-sync.log`
- **Format**: Timestamped entries with detailed information
- **Rotation**: Automatic when file exceeds 1MB

### GitHub Actions Reports
- **Location**: Workflow run artifacts
- **Content**: Sync status, timestamps, change counts
- **Retention**: 7 days

## 🎯 Best Practices

1. **Regular Monitoring**: Check status weekly
2. **Log Review**: Monitor logs for any issues
3. **Manual Commits**: Still use manual commits for major changes
4. **Tag Management**: Review auto-generated tags
5. **Backup Verification**: Ensure GitHub has latest changes

---

**Note**: This system is designed to complement, not replace, proper version control practices. Always review auto-commits and use manual commits for significant changes.
