#!/usr/bin/env bash

if [ "$1" = "" ]; then
    echo "ERROR: paramater needed"
    exit 2
fi

INPUT=$1
ROOTDIR=$(git rev-parse --show-toplevel || echo ".")
if [ "$PWD" != "$ROOTDIR" ]; then
    # shellcheck disable=SC2164
    cd "$ROOTDIR";
fi

get_docker_md5() {
  docker_md5=$(find build .github/data/version.txt -type f ! -name "*.md" -exec md5sum {} + | LC_ALL=C sort  | md5sum | awk '{ print $1 }')
  echo "${docker_md5:0:8}"
}

get_go_code_md5() {
  find . -type f \( -name "*.go" -o -name go.mod -o -name go.sum -o -name "*.tmpl" -o -name "version.txt" \) -not -path "./docs*"  -exec md5sum {} + | LC_ALL=C sort  | md5sum | awk '{ print $1 }'
}

get_tests_md5() {
  find tests perf-tests .github/data/version.txt -type f -exec md5sum {} + | LC_ALL=C sort  | md5sum | awk '{ print $1 }'
}

get_chart_md5() {
  find charts .github/data/version.txt -type f -exec md5sum {} + | LC_ALL=C sort  | md5sum | awk '{ print $1 }'
}

get_actions_md5() {
  find .github .github/data/version.txt -type f -exec md5sum {} + | LC_ALL=C sort  | md5sum | awk '{ print $1 }'
}

get_build_tag() {
  echo "$(get_docker_md5) $(get_go_code_md5)" | md5sum | awk '{ print $1 }'
}

get_stable_tag() {
  echo "$(get_build_tag) $(get_tests_md5) $(get_chart_md5) $(get_actions_md5)" | md5sum | awk '{ print $1 }'
}

case $INPUT in
  docker_md5)
    echo "docker_md5=$(get_docker_md5)"
    ;;

  go_code_md5)
    echo "go_code_md5=$(get_go_code_md5)"
    ;;

  build_tag)
    echo "build_tag=$(get_build_tag)"
    ;;

  stable_tag)
    echo "stable_tag=$(get_stable_tag)"
    ;;

  *)
    echo "ERROR: option not found"
    exit 2
    ;;
esac
