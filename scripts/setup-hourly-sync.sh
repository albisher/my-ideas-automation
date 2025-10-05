#!/bin/bash

# Setup script for hourly auto-sync
# This script configures both GitHub Actions and local cron job

set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT_NAME="$(basename "$0")"

echo "🔄 Setting up hourly auto-sync for repository: $REPO_DIR"

# Function to check if GitHub CLI is available
check_gh_cli() {
    if ! command -v gh &> /dev/null; then
        echo "❌ GitHub CLI (gh) not found. Please install it first:"
        echo "   brew install gh  # macOS"
        echo "   apt install gh   # Ubuntu/Debian"
        echo "   choco install gh # Windows"
        return 1
    fi
    return 0
}

# Function to check GitHub Actions permissions
check_github_permissions() {
    echo "🔐 Checking GitHub Actions permissions..."
    
    if ! gh auth status &> /dev/null; then
        echo "❌ Not authenticated with GitHub. Please run: gh auth login"
        return 1
    fi
    
    # Check if we can access the repository
    if ! gh repo view &> /dev/null; then
        echo "❌ Cannot access repository. Please check permissions."
        return 1
    fi
    
    echo "✅ GitHub authentication verified"
    return 0
}

# Function to enable GitHub Actions
enable_github_actions() {
    echo "🚀 Enabling GitHub Actions workflow..."
    
    # Check if workflow file exists
    if [ ! -f ".github/workflows/hourly-sync.yml" ]; then
        echo "❌ Hourly sync workflow not found. Please ensure .github/workflows/hourly-sync.yml exists."
        return 1
    fi
    
    # Enable GitHub Actions if disabled
    gh api repos/:owner/:repo/actions/permissions --method PUT --field enabled=true &> /dev/null || true
    
    echo "✅ GitHub Actions workflow enabled"
    echo "📋 Workflow will run every hour automatically"
}

# Function to setup local cron job
setup_local_cron() {
    echo "⏰ Setting up local cron job..."
    
    # Make auto-sync script executable
    chmod +x scripts/auto-sync.sh
    
    # Setup cron job
    ./scripts/auto-sync.sh setup-cron
    
    echo "✅ Local cron job configured"
    echo "📋 Will run every hour: 0 * * * *"
}

# Function to test the setup
test_setup() {
    echo "🧪 Testing auto-sync setup..."
    
    # Test the auto-sync script
    if ./scripts/auto-sync.sh; then
        echo "✅ Auto-sync script test passed"
    else
        echo "❌ Auto-sync script test failed"
        return 1
    fi
    
    # Check cron job
    if crontab -l 2>/dev/null | grep -q "auto-sync.sh"; then
        echo "✅ Cron job is active"
    else
        echo "❌ Cron job not found"
        return 1
    fi
}

# Function to show status
show_status() {
    echo ""
    echo "📊 Auto-sync Status:"
    echo "==================="
    
    # GitHub Actions status
    echo "🌐 GitHub Actions:"
    if [ -f ".github/workflows/hourly-sync.yml" ]; then
        echo "   ✅ Workflow file exists"
        echo "   📅 Schedule: Every hour (0 * * * *)"
        echo "   🔗 View: https://github.com/$(gh repo view --json owner,name -q '.owner.login + "/" + .name')/actions"
    else
        echo "   ❌ Workflow file missing"
    fi
    
    # Local cron status
    echo ""
    echo "💻 Local Cron:"
    if crontab -l 2>/dev/null | grep -q "auto-sync.sh"; then
        echo "   ✅ Cron job active"
        crontab -l | grep "auto-sync.sh" | sed 's/^/   📅 /'
    else
        echo "   ❌ No cron job found"
    fi
    
    # Log file status
    echo ""
    echo "📝 Logs:"
    if [ -f ".taskmaster/logs/auto-sync.log" ]; then
        echo "   ✅ Log file exists: .taskmaster/logs/auto-sync.log"
        echo "   📊 Size: $(du -h .taskmaster/logs/auto-sync.log 2>/dev/null | cut -f1 || echo 'Unknown')"
    else
        echo "   ℹ️  No log file yet (will be created on first run)"
    fi
}

# Function to show usage
show_usage() {
    echo "Usage: $SCRIPT_NAME [command]"
    echo ""
    echo "Commands:"
    echo "  setup     - Setup both GitHub Actions and local cron (default)"
    echo "  github    - Setup only GitHub Actions"
    echo "  local     - Setup only local cron"
    echo "  test      - Test the current setup"
    echo "  status    - Show current status"
    echo "  remove    - Remove local cron job"
    echo "  help      - Show this help"
}

# Main execution
main() {
    case "${1:-setup}" in
        "setup")
            echo "🔧 Setting up complete hourly auto-sync..."
            
            if check_gh_cli && check_github_permissions; then
                enable_github_actions
            else
                echo "⚠️  Skipping GitHub Actions setup (check requirements above)"
            fi
            
            setup_local_cron
            test_setup
            show_status
            ;;
        "github")
            echo "🌐 Setting up GitHub Actions only..."
            if check_gh_cli && check_github_permissions; then
                enable_github_actions
                show_status
            fi
            ;;
        "local")
            echo "💻 Setting up local cron only..."
            setup_local_cron
            test_setup
            show_status
            ;;
        "test")
            test_setup
            show_status
            ;;
        "status")
            show_status
            ;;
        "remove")
            echo "🗑️  Removing local cron job..."
            ./scripts/auto-sync.sh remove-cron
            echo "✅ Local cron job removed"
            ;;
        "help"|"-h"|"--help")
            show_usage
            ;;
        *)
            echo "❌ Unknown command: $1"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
