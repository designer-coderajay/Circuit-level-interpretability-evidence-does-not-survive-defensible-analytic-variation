#!/usr/bin/env bash
# Commit helper. Clears the stale index.lock first.
#
# Why this exists. This repo lives under ~/Desktop, which Spotlight indexes, and
# is usually open in an editor with git integration. Both take the git index
# lock periodically. When one of them holds it as git tries to write, git aborts
# with "Unable to create .git/index.lock: File exists" and leaves the file
# behind, so every later commit fails too until it is removed by hand.
#
# `lsof .git/index.lock` identified the holder as a `com.apple` process on
# 2026-08-04. Removing the lock is safe whenever no git command is actually
# running, which this script checks.
#
# Usage:  ./scripts/commit.sh "message"
set -euo pipefail

cd "$(dirname "$0")/.."

if pgrep -x git >/dev/null 2>&1; then
  echo "A real git process is running. Not touching the lock. Try again shortly." >&2
  exit 1
fi

[ -f .git/index.lock ] && { echo "clearing stale .git/index.lock"; rm -f .git/index.lock; }
[ -f .git/HEAD.lock ]  && rm -f .git/HEAD.lock

git add -A
if git diff --cached --quiet; then
  echo "nothing staged; working tree clean"
  exit 0
fi
git commit -m "${1:?usage: ./scripts/commit.sh \"message\"}"
git --no-pager log --oneline -1
