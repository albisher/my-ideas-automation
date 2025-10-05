#!/bin/bash

# Automatic Tag Creation Script
# This script creates a new tag based on the latest tag and pushes it to GitHub

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Automatic Tag Creation Script${NC}"
echo "=================================="

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}❌ Error: Not in a git repository${NC}"
    exit 1
fi

# Check if we have any commits
if ! git rev-parse HEAD > /dev/null 2>&1; then
    echo -e "${RED}❌ Error: No commits found${NC}"
    exit 1
fi

# Get the latest tag
LATEST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
echo -e "${YELLOW}📋 Current latest tag: ${LATEST_TAG}${NC}"

# Parse version number
VERSION=${LATEST_TAG#v}
IFS='.' read -r MAJOR MINOR PATCH <<< "$VERSION"

# Determine what type of version bump to make
echo ""
echo "What type of version bump would you like?"
echo "1) Patch (${MAJOR}.${MINOR}.$((PATCH + 1))) - Bug fixes, minor changes"
echo "2) Minor (${MAJOR}.$((MINOR + 1)).0) - New features, backward compatible"
echo "3) Major ($((MAJOR + 1)).0.0) - Breaking changes"
echo "4) Custom version"
echo "5) Exit"

read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        PATCH=$((PATCH + 1))
        NEW_TAG="v${MAJOR}.${MINOR}.${PATCH}"
        ;;
    2)
        MINOR=$((MINOR + 1))
        PATCH=0
        NEW_TAG="v${MAJOR}.${MINOR}.${PATCH}"
        ;;
    3)
        MAJOR=$((MAJOR + 1))
        MINOR=0
        PATCH=0
        NEW_TAG="v${MAJOR}.${MINOR}.${PATCH}"
        ;;
    4)
        read -p "Enter custom version (e.g., v1.2.3): " NEW_TAG
        if [[ ! $NEW_TAG =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
            echo -e "${RED}❌ Error: Invalid version format. Use format like v1.2.3${NC}"
            exit 1
        fi
        ;;
    5)
        echo -e "${YELLOW}👋 Exiting...${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}❌ Error: Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${YELLOW}📝 Creating tag: ${NEW_TAG}${NC}"

# Check if tag already exists
if git tag -l | grep -q "^${NEW_TAG}$"; then
    echo -e "${RED}❌ Error: Tag ${NEW_TAG} already exists${NC}"
    exit 1
fi

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

Generated automatically by create-tag.sh"

git tag -a "${NEW_TAG}" -m "${TAG_MESSAGE}"

echo -e "${GREEN}✅ Tag ${NEW_TAG} created successfully${NC}"

# Ask if user wants to push to remote
echo ""
read -p "Do you want to push the tag to remote? (y/N): " push_choice

if [[ $push_choice =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}📤 Pushing tag to remote...${NC}"
    git push origin "${NEW_TAG}"
    echo -e "${GREEN}✅ Tag ${NEW_TAG} pushed to remote${NC}"
    
    # Ask if user wants to create a GitHub release
    echo ""
    read -p "Do you want to create a GitHub release? (y/N): " release_choice
    
    if [[ $release_choice =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}📦 Creating GitHub release...${NC}"
        
        # Check if gh CLI is available
        if command -v gh &> /dev/null; then
            gh release create "${NEW_TAG}" \
                --title "Release ${NEW_TAG}" \
                --notes "${TAG_MESSAGE}" \
                --latest
            echo -e "${GREEN}✅ GitHub release created successfully${NC}"
        else
            echo -e "${YELLOW}⚠️  GitHub CLI not found. Please create the release manually at:${NC}"
            echo -e "${BLUE}   https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\([^/]*\/[^/]*\)\.git/\1/')/releases/new${NC}"
        fi
    fi
else
    echo -e "${YELLOW}⚠️  Tag created locally but not pushed to remote${NC}"
    echo -e "${BLUE}💡 To push later, run: git push origin ${NEW_TAG}${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Tag creation process completed!${NC}"
echo -e "${BLUE}📋 Summary:${NC}"
echo -e "   Previous tag: ${LATEST_TAG}"
echo -e "   New tag: ${NEW_TAG}"
echo -e "   Tag message: ${TAG_MESSAGE}"
