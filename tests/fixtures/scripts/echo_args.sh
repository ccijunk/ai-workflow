#!/bin/bash
set -euo pipefail

for arg in "$@"; do
  echo "ARG: $arg"
done
echo "RUN_DIR: $RUN_DIR"
exit 0