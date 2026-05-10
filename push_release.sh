#!/bin/bash

set -e

echo "======================================="
echo " Raspberry Pi Kiosk Release Tool"
echo "======================================="
echo ""

# ---------------------------------------
# Ensure git repo
# ---------------------------------------

if [ ! -d ".git" ]; then
    echo "ERROR: Not a git repository."
    exit 1
fi

# ---------------------------------------
# Ensure stable branch exists
# ---------------------------------------

if ! git show-ref --verify --quiet refs/heads/stable; then
    echo "ERROR: Stable branch does not exist."
    echo ""
    echo "Create it once using:"
    echo "git checkout main"
    echo "git checkout -b stable"
    echo "git push -u origin stable"
    exit 1
fi

# ---------------------------------------
# Force to main branch first
# ---------------------------------------

git checkout main

# ---------------------------------------
# Show current version
# ---------------------------------------

if [ -f "version.txt" ]; then
    CURRENT_VERSION=$(cat version.txt)
else
    CURRENT_VERSION="unknown"
fi

echo "Current Version: $CURRENT_VERSION"
echo ""

# ---------------------------------------
# Git status
# ---------------------------------------

git status

echo ""

# ---------------------------------------
# Commit message
# ---------------------------------------

read -p "Enter commit message: " COMMIT_MESSAGE

if [ -z "$COMMIT_MESSAGE" ]; then
    echo "Commit message cannot be empty."
    exit 1
fi

# ---------------------------------------
# Version number
# ---------------------------------------

read -p "Enter version number (example 1.5.0): " VERSION

if [ -z "$VERSION" ]; then
    echo "Version cannot be empty."
    exit 1
fi

echo "$VERSION" > version.txt

# ---------------------------------------
# Release target
# ---------------------------------------

echo ""
echo "Release target:"
echo "1) main"
echo "2) stable"
echo ""

read -p "Choice: " TARGET

case $TARGET in
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

# ---------------------------------------
# Commit changes to main
# ---------------------------------------

echo ""
echo "======================================="
echo " Committing Changes to MAIN"
echo "======================================="

git add .

if [[ -n $(git status --porcelain) ]]; then
    git commit -m "$COMMIT_MESSAGE"
else
    echo "No changes to commit."
fi

# ---------------------------------------
# Push main
# ---------------------------------------

echo ""
echo "======================================="
echo " Pushing MAIN"
echo "======================================="

git pull origin main
git push origin main

# ---------------------------------------
# MAIN release only
# ---------------------------------------

if [ "$TARGET_BRANCH" = "main" ]; then

    echo ""
    echo "======================================="
    echo " MAIN Release Complete"
    echo "======================================="
    echo ""
    echo "Version: v$VERSION"
    echo ""

    exit 0
fi

# ---------------------------------------
# STABLE release flow
# ---------------------------------------

echo ""
echo "======================================="
echo " Updating STABLE"
echo "======================================="

git checkout stable

git pull origin stable

git merge main

# ---------------------------------------
# Create tag
# ---------------------------------------

echo ""
echo "======================================="
echo " Creating Tag"
echo "======================================="

git tag "v$VERSION"

# ---------------------------------------
# Push stable
# ---------------------------------------

echo ""
echo "======================================="
echo " Pushing STABLE"
echo "======================================="

git push origin stable

# ---------------------------------------
# Push tag
# ---------------------------------------

echo ""
echo "======================================="
echo " Pushing Tag"
echo "======================================="

git push origin "v$VERSION"

# ---------------------------------------
# Return to main
# ---------------------------------------

git checkout main

# ---------------------------------------
# Done
# ---------------------------------------

echo ""
echo "======================================="
echo " STABLE Release Complete"
echo "======================================="
echo ""
echo "Version: v$VERSION"
echo ""