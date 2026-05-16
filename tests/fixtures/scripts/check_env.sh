#!/bin/bash
set -euo pipefail

if [ -z "$RUN_DIR" ]; then
  echo "Error: RUN_DIR not set" >&2
  exit 1
fi
echo "$RUN_DIR" > "$RUN_DIR/run_dir.txt"
exit 0