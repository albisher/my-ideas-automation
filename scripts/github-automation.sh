#!/bin/bash

# GitHub Automation Script
# This script handles all GitHub operations including pushing, tagging, and automation setup

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${PURPLE}🤖 GitHub Automation Script${NC}"
echo "=============================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check git status
check_git_status() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        echo -e "${RED}❌ Error: Not in a git repository${NC}"
        exit 1
    fi
    
    if [ -n "$(git status --porcelain)" ]; then
        echo -e "${YELLOW}⚠️  You have uncommitted changes. Please commit them first.${NC}"
        git status --short
        echo ""
        read -p "Do you want to commit all changes? (y/N): " commit_choice
        if [[ $commit_choice =~ ^[Yy]$ ]]; then
            git add .
            read -p "Enter commit message: " commit_msg
            git commit -m "$commit_msg"
            echo -e "${GREEN}✅ Changes committed${NC}"
        else
            echo -e "${RED}❌ Please commit your changes first${NC}"
            exit 1
        fi
    fi
}

# Function to push to GitHub
push_to_github() {
    echo -e "${BLUE}📤 Pushing to GitHub...${NC}"
    
    # Check if remote exists
    if ! git remote get-url origin > /dev/null 2>&1; then
        echo -e "${RED}❌ No remote origin found. Please set up a remote repository first.${NC}"
        exit 1
    fi
    
    # Push to main branch
    git push origin main
    
    # Push all tags
    if [ -n "$(git tag -l)" ]; then
        git push origin --tags
        echo -e "${GREEN}✅ All tags pushed to GitHub${NC}"
    fi
    
    echo -e "${GREEN}✅ Successfully pushed to GitHub${NC}"
}

# Function to create and push tag
create_tag() {
    echo -e "${BLUE}🏷️  Creating tag...${NC}"
    
    # Get the latest tag
    LATEST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
    echo -e "${YELLOW}📋 Current latest tag: ${LATEST_TAG}${NC}"
    
    # Parse version number
    VERSION=${LATEST_TAG#v}
    IFS='.' read -r MAJOR MINOR PATCH <<< "$VERSION"
    
    # Increment patch version
    PATCH=$((PATCH + 1))
    NEW_TAG="v${MAJOR}.${MINOR}.${PATCH}"
    
    echo -e "${YELLOW}📝 Creating tag: ${NEW_TAG}${NC}"
    
    # Get commit messages since last tag for changelog
    if [ "$LATEST_TAG" != "v0.0.0" ]; then
        CHANGELOG=$(git log --pretty=format:"- %s" ${LATEST_TAG}..HEAD)
    else
        CHANGELOG=$(git log --pretty=format:"- %s" --max-count=20)
    fi
    
    # Create the tag with a message
    TAG_MESSAGE="Release ${NEW_TAG}

Changes in this release:
${CHANGELOG}

Generated automatically by github-automation.sh"

    git tag -a "${NEW_TAG}" -m "${TAG_MESSAGE}"
    git push origin "${NEW_TAG}"
    
    echo -e "${GREEN}✅ Tag ${NEW_TAG} created and pushed${NC}"
}

# Function to create GitHub release
create_release() {
    if command_exists gh; then
        echo -e "${BLUE}📦 Creating GitHub release...${NC}"
        
        # Get the latest tag
        LATEST_TAG=$(git describe --tags --abbrev=0)
        
        # Create release
        gh release create "${LATEST_TAG}" \
            --title "Release ${LATEST_TAG}" \
            --notes "$(git tag -l --format='%(contents)' "${LATEST_TAG}")" \
            --latest
        
        echo -e "${GREEN}✅ GitHub release created${NC}"
    else
        echo -e "${YELLOW}⚠️  GitHub CLI not found. Please install it to create releases automatically.${NC}"
        echo -e "${BLUE}💡 Install with: brew install gh${NC}"
    fi
}

# Function to set up GitHub Actions
setup_github_actions() {
    echo -e "${BLUE}⚙️  Setting up GitHub Actions...${NC}"
    
    # Create .github directory if it doesn't exist
    mkdir -p .github/workflows
    
    # Check if automation workflow exists
    if [ ! -f ".github/workflows/automation.yml" ]; then
        echo -e "${YELLOW}⚠️  GitHub Actions workflow not found. Please run the main setup first.${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✅ GitHub Actions workflow is configured${NC}"
    echo -e "${BLUE}📋 The workflow will automatically:${NC}"
    echo "   - Create tags on pushes to main"
    echo "   - Generate releases"
    echo "   - Manage issues and project status"
    echo "   - Run security scans"
    echo "   - Update documentation"
}

# Function to check repository status
check_repo_status() {
    echo -e "${BLUE}🔍 Checking repository status...${NC}"
    
    # Check if we're on main branch
    CURRENT_BRANCH=$(git branch --show-current)
    if [ "$CURRENT_BRANCH" != "main" ]; then
        echo -e "${YELLOW}⚠️  You're on branch '${CURRENT_BRANCH}', not 'main'${NC}"
        read -p "Do you want to switch to main branch? (y/N): " switch_choice
        if [[ $switch_choice =~ ^[Yy]$ ]]; then
            git checkout main
        fi
    fi
    
    # Check remote status
    if git remote get-url origin > /dev/null 2>&1; then
        REMOTE_URL=$(git remote get-url origin)
        echo -e "${GREEN}✅ Remote origin: ${REMOTE_URL}${NC}"
    else
        echo -e "${RED}❌ No remote origin configured${NC}"
        return 1
    fi
    
    # Check for unpushed commits
    if [ -n "$(git log origin/main..HEAD 2>/dev/null)" ]; then
        echo -e "${YELLOW}⚠️  You have unpushed commits${NC}"
    else
        echo -e "${GREEN}✅ All commits are pushed${NC}"
    fi
}

# Main menu
show_menu() {
    echo ""
    echo -e "${PURPLE}What would you like to do?${NC}"
    echo "1) Check repository status"
    echo "2) Push all changes to GitHub"
    echo "3) Create and push a new tag"
    echo "4) Create GitHub release"
    echo "5) Set up GitHub Actions"
    echo "6) Full automation (push + tag + release)"
    echo "7) Exit"
    echo ""
}

# Main execution
main() {
    check_git_status
    
    while true; do
        show_menu
        read -p "Enter your choice (1-7): " choice
        
        case $choice in
            1)
                check_repo_status
                ;;
            2)
                push_to_github
                ;;
            3)
                create_tag
                ;;
            4)
                create_release
                ;;
            5)
                setup_github_actions
                ;;
            6)
                echo -e "${PURPLE}🚀 Running full automation...${NC}"
                push_to_github
                create_tag
                create_release
                echo -e "${GREEN}🎉 Full automation completed!${NC}"
                ;;
            7)
                echo -e "${GREEN}👋 Goodbye!${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}❌ Invalid choice. Please try again.${NC}"
                ;;
        esac
        
        echo ""
        read -p "Press Enter to continue..."
    done
}

# Run main function
main
