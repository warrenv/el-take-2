#!/usr/bin/env bash

# This script updates a repo's submodule to the latest commit.
#
# - clone repo
# - init submodule
# - create branch
# - update submodules
# - if status change
#   - commit
#   - push commit to branch
#   - print the branch name for the caller to use.

readonly repo_url=$(echo $1 | sed -e 's|\.git$||')
readonly submodule_name=$2
readonly branch_name="submodules/${submodule_name}-$RANDOM"
readonly tmp_dir=$(mktemp -d -t $(basename $0)-XXXXXXXXXX)

# Check args
if [ -z "$repo_url" -o -z "$submodule_name" ]; then
  echo "usage: $(basename $0) REPO_URL SUBMODULE_NAME"
  exit 1
fi

# Do everything in a temp dir.
if cd $tmp_dir 2>/dev/null; then
  git clone --quiet $repo_url

  if cd $(basename $repo_url) 2>/dev/null; then
    (
      git submodule update --init $submodule_name
      git submodule update --remote $submodule_name
    ) >/dev/null 2>&1

    if git status | grep '^nothing to commit,' >/dev/null 2>&1; then
      echo "No updates for $submodule_name"
      exit 1
    fi

    (
      git co -b $branch_name
      git add .
      git commit -a -m "Update submodule $submodule_name to latest"
      git push origin $branch_name
    ) >/dev/null 2>&1

    if [ $? -eq 0 ]; then
      # cleanup
      cd
      rm -rf $tmp_dir >/dev/null 2>&1

      echo $branch_name
      exit 0
    else
      exit 3
    fi
  else
    echo "Cannot cd to ${tmp_dir}/$(basename $repo_url)"
    exit 2
  fi
else
  echo "Cannot cd to ${tmp_dir}"
  exit 2
fi

exit 0
