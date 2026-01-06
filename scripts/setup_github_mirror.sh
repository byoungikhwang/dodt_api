#!/usr/bin/env bash
# scripts/setup_github_mirror.sh
# Usage:
#   1) Authenticate with GitHub CLI as the target account (saintjin9@gmail.com):
#        gh auth login
#   2) (Optional) Create a remote repo with gh:
#        gh repo create saintjin9/REPO_NAME --public --source=. --remote=mirror --push
#   3) Or provide an existing remote URL and push mirror:
#        ./scripts/setup_github_mirror.sh git@github.com:saintjin9/REPO.git

set -euo pipefail

if ! command -v git >/dev/null 2>&1; then
  echo "git is required. Install git and try again." >&2
  exit 1
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "gh (GitHub CLI) not found. You can still push to a remote URL, but for repo creation please install gh." >&2
fi

REMOTE_URL="$1"
if [ -z "$REMOTE_URL" ]; then
  echo "Usage: $0 <remote-git-url>" >&2
  echo "Example: $0 git@github.com:saintjin9/my-repo.git" >&2
  exit 2
fi

# Add or update remote named 'mirror'
if git remote get-url mirror >/dev/null 2>&1; then
  echo "Updating existing remote 'mirror' to $REMOTE_URL"
  git remote set-url mirror "$REMOTE_URL"
else
  echo "Adding remote 'mirror' -> $REMOTE_URL"
  git remote add mirror "$REMOTE_URL"
fi

# Push mirror (all refs, tags, branches)
echo "Pushing --mirror to 'mirror' (this may take a while)..."
# Note: user must be authenticated; if using HTTPS with token, prefer credential helper or gh auth login.
git push --mirror mirror

echo "Mirror push completed. Verify repository on GitHub (https://github.com/)."

echo "If you need to create the remote repository from this machine using gh, you can run:"
echo "  gh repo create <owner/repo> --public --source=. --remote=mirror --push"

echo "To authenticate as saintjin9@gmail.com, run:"
echo "  gh auth login --with-token"
echo "and provide a personal access token that has repo permissions."
