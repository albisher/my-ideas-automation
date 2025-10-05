# GitHub Automation Setup

This repository is configured with comprehensive automation for GitHub operations including automatic tagging, releases, issue management, and project monitoring.

## 🚀 Quick Start

### 1. Initial Setup
```bash
# Make scripts executable
chmod +x scripts/*.sh

# Run the automation script
./scripts/github-automation.sh
```

### 2. Manual Operations
```bash
# Push all changes and create tag
git add .
git commit -m "Your changes"
git push origin main
./scripts/create-tag.sh
```

## 📋 Automation Features

### Automatic Tagging
- **Trigger**: Every push to `main` branch
- **Action**: Creates incremental version tags (v1.0.0, v1.0.1, etc.)
- **Location**: `.github/workflows/automation.yml`

### Release Management
- **Automatic**: Creates GitHub releases for each tag
- **Changelog**: Generates changelog from commit messages
- **Features**: Includes project structure and recent updates

### Issue Management
- **Project Status**: Automatically creates/updates project status issues
- **Dependency Analysis**: Monitors and reports on project dependencies
- **Security**: Runs vulnerability scans and reports findings

### Documentation Updates
- **Auto-generated**: Updates project documentation
- **Structure**: Lists all projects and recent changes
- **Commit**: Automatically commits documentation updates

## 🛠️ Scripts Available

### `scripts/github-automation.sh`
Comprehensive automation script with menu-driven interface:
- Check repository status
- Push changes to GitHub
- Create and push tags
- Create GitHub releases
- Set up GitHub Actions
- Full automation workflow

### `scripts/create-tag.sh`
Interactive tag creation script:
- Version bump options (patch/minor/major)
- Custom version input
- Automatic changelog generation
- GitHub release creation

## 🔧 GitHub Actions Workflow

The automation is powered by GitHub Actions with the following jobs:

### `auto-tag`
- Runs on every push to main
- Creates incremental version tags
- Pushes tags to remote repository

### `create-release`
- Triggers after tag creation
- Generates changelog from commits
- Creates GitHub release with full details

### `issue-management`
- Analyzes project structure
- Creates/updates project status issues
- Monitors project health

### `dependency-check`
- Scans for dependency files
- Creates dependency analysis issues
- Monitors for outdated packages

### `security-scan`
- Runs Trivy vulnerability scanner
- Uploads results to GitHub Security tab
- Monitors for security issues

### `documentation-update`
- Generates comprehensive project docs
- Updates PROJECT_DOCS.md
- Commits documentation changes

## 📊 Project Structure

This repository contains:

- **Home Assistant**: Complete configuration and automations
- **Matter Integration**: Smart home protocol setup
- **DCS-8000LH Camera**: Open source camera project with defogger tools
- **ESP32 Smart Speaker**: IoT audio device implementation
- **USB Remote TV Control**: IR control system
- **Xiaomi L05G**: IR control customization
- **Documentation**: Comprehensive guides and working methods

## 🔄 Automation Workflow

1. **Code Changes**: Developer makes changes and commits
2. **Push to Main**: Changes are pushed to main branch
3. **Auto Tag**: GitHub Actions creates new version tag
4. **Auto Release**: GitHub release is created with changelog
5. **Issue Updates**: Project status and dependency issues are updated
6. **Security Scan**: Vulnerability scan runs automatically
7. **Documentation**: Project docs are updated automatically

## 🎯 Benefits

- **Consistency**: Standardized versioning and release process
- **Automation**: Reduces manual work and human error
- **Visibility**: Clear project status and recent changes
- **Security**: Automated vulnerability scanning
- **Documentation**: Always up-to-date project information
- **Monitoring**: Continuous project health monitoring

## 🚨 Troubleshooting

### Common Issues

1. **Tag Creation Fails**
   ```bash
   # Check if tag already exists
   git tag -l | grep v1.0.0
   
   # Delete local tag if needed
   git tag -d v1.0.0
   ```

2. **Push Fails**
   ```bash
   # Check remote configuration
   git remote -v
   
   # Update remote URL if needed
   git remote set-url origin https://github.com/username/repo.git
   ```

3. **GitHub Actions Not Running**
   - Check repository permissions
   - Verify workflow file syntax
   - Check GitHub Actions tab for errors

### Manual Override

If automation fails, you can manually:

```bash
# Create tag manually
git tag -a v1.0.0 -m "Manual release"
git push origin v1.0.0

# Create release manually
gh release create v1.0.0 --title "Release v1.0.0" --notes "Manual release"
```

## 📈 Monitoring

The automation system provides:

- **Project Status Issues**: Track overall project health
- **Dependency Reports**: Monitor outdated dependencies
- **Security Alerts**: Vulnerability notifications
- **Release History**: Complete version history
- **Documentation**: Always current project docs

## 🔗 Links

- **Repository**: https://github.com/albisher/my-ideas-automation
- **Actions**: https://github.com/albisher/my-ideas-automation/actions
- **Releases**: https://github.com/albisher/my-ideas-automation/releases
- **Issues**: https://github.com/albisher/my-ideas-automation/issues

---

*This automation system ensures your project stays organized, secure, and well-documented with minimal manual intervention.*
