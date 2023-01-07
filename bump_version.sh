#!/usr/bin/env bash

# bump_version.sh (show|major|minor|patch|prerelease|build)

set -o nounset
set -o errexit
set -o pipefail

VERSION_FILE=src/findcdn/_version.py

HELP_INFORMATION="bump_version.sh (show|major|minor|patch|prerelease|build|finalize)"

old_version=$(sed -n "s/^__version__ = \"\(.*\)\"$/\1/p" $VERSION_FILE)
# Comment out periods so they are interpreted as periods and don't
# just match any character
old_version_regex=${old_version//\./\\\.}

if [ $# -ne 1 ]; then
  echo "$HELP_INFORMATION"
else
  case $1 in
    major | minor | patch | prerelease | build)
      new_version=$(python -c "import semver; print(semver.bump_$1('$old_version'))")
      echo Changing version from "$old_version" to "$new_version"
      # A temp file is used to provide compatability with macOS development
      # as a result of macOS using the BSD version of sed
      tmp_file=/tmp/version.$$
      sed "s/$old_version_regex/$new_version/" $VERSION_FILE > $tmp_file
      mv $tmp_file $VERSION_FILE
      git add $VERSION_FILE
      git commit -m"Bump version from $old_version to $new_version"
      git push
      ;;
    finalize)
      new_version=$(python -c "import semver; print(semver.finalize_version('$old_version'))")
      echo Changing version from "$old_version" to "$new_version"
      # A temp file is used to provide compatability with macOS development
      # as a result of macOS using the BSD version of sed
      tmp_file=/tmp/version.$$
      sed "s/$old_version_regex/$new_version/" $VERSION_FILE > $tmp_file
      mv $tmp_file $VERSION_FILE
      git add $VERSION_FILE
      git commit -m"Finalize version from $old_version to $new_version"
      git push
      ;;
    show)
      echo "$old_version"
      ;;
    *)
      echo "$HELP_INFORMATION"
      ;;
  esac
fi
