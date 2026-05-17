#!/bin/bash
set -eo pipefail

echo "Script executed successfully"
if [ -n "$1" ]; then
  echo "ARG1: $1"
fi
if [ -n "$2" ]; then
  echo "ARG2: $2"
fi
echo "test output" > "$RUN_DIR/output.txt"
exit 0