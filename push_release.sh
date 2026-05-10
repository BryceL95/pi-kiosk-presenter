#!/bin/bash

set -e

echo "======================================="
echo " Raspberry Pi Kiosk Release Tool"
echo "======================================="
echo ""

# ---------------------------------------
# Ensure we're in a git repo
# ---------------------------------------

if [ ! -d ".git" ]; then
    echo "ERROR: This is not a git repository."
    exit 1
fi

# ---------------------------------------
# Show current branch/version
# ---------------------------------------

CURRENT_BRANCH=$(git branch --show-current)

if [ -f "version.txt" ]; then
    CURRENT_VERSION=$(cat version.txt)
else
    CURRENT_VERSION="unknown"
fi

echo "Current Branch : $CURRENT_BRANCH"
echo "Current Version: $CURRENT_VERSION"
echo ""

# ---------------------------------------
# Ask release type
# ---------------------------------------

echo "Select release branch:"
echo "1) main"
echo "2) stable"
echo ""

read -p "Choice: " BRANCH_CHOICE

case $BRANCH_CHOICE in
    1)
        TARGET_BRANCH="main"
        ;;
    2)
        TARGET_BRANCH="stable"
        ;;
    *)
        echo "Invalid selection."
        exit 1
        ;;
esac

echo ""
echo "Target Branch: $TARGET_BRANCH"
echo ""

# ---------------------------------------
# Ask version
# ---------------------------------------

read -p "Enter new version number (example 1.5.0): " VERSION

if [ -z "$VERSION" ]; then
    echo "Version cannot be empty."
    exit 1
fi

echo ""
echo "New Version: $VERSION"
echo ""

# ---------------------------------------
# Ask commit message
# ---------------------------------------

read -p "Enter release notes / commit message: " RELEASE_MESSAGE

if [ -z "$RELEASE_MESSAGE" ]; then
    RELEASE_MESSAGE="Release v$VERSION"
fi

FULL_COMMIT_MESSAGE="Release v$VERSION - $RELEASE_MESSAGE"

echo ""
echo "Commit Message:"
echo "$FULL_COMMIT_MESSAGE"
echo ""

# ---------------------------------------
# Confirm
# ---------------------------------------

echo "======================================="
echo " Summary"
echo "======================================="
echo "Branch : $TARGET_BRANCH"
echo "Version: $VERSION"
echo "Message: $FULL_COMMIT_MESSAGE"
echo ""

read -p "Continue? (y/n): " CONFIRM

if [[ "$CONFIRM" != "y" && "$CONFIRM" != "Y" ]]; then
    echo "Cancelled."
    exit 0
fi

# ---------------------------------------
# Checkout target branch
# ---------------------------------------

echo ""
echo "======================================="
echo " Switching Branch"
echo "======================================="

git checkout $TARGET_BRANCH

# ---------------------------------------
# Pull latest changes
# ---------------------------------------

echo ""
echo "======================================="
echo " Pulling Latest Changes"
echo "======================================="

git pull --rebase origin $TARGET_BRANCH

# ---------------------------------------
# Update version.txt
# ---------------------------------------

echo ""
echo "======================================="
echo " Updating version.txt"
echo "======================================="

echo "$VERSION" > version.txt

# ---------------------------------------
# Show git status
# ---------------------------------------

echo ""
echo "======================================="
echo " Git Status"
echo "======================================="

git status

echo ""

read -p "Proceed with commit? (y/n): " COMMIT_CONFIRM

if [[ "$COMMIT_CONFIRM" != "y" && "$COMMIT_CONFIRM" != "Y" ]]; then
    echo "Cancelled."
    exit 0
fi

# ---------------------------------------
# Commit changes
# ---------------------------------------

echo ""
echo "======================================="
echo " Committing Changes"
echo "======================================="

git add .

git commit -m "$FULL_COMMIT_MESSAGE"

# ---------------------------------------
# Create git tag
# ---------------------------------------

echo ""
echo "======================================="
echo " Creating Tag"
echo "======================================="

git tag "v$VERSION"

# ---------------------------------------
# Push branch
# ---------------------------------------

echo ""
echo "======================================="
echo " Pushing Branch"
echo "======================================="

git push origin $TARGET_BRANCH

# ---------------------------------------
# Push tag
# ---------------------------------------

echo ""
echo "======================================="
echo " Pushing Tag"
echo "======================================="

git push origin "v$VERSION"

# ---------------------------------------
# Complete
# ---------------------------------------

echo ""
echo "======================================="
echo " Release Complete"
echo "======================================="
echo ""
echo "Branch : $TARGET_BRANCH"
echo "Version: v$VERSION"
echo ""
