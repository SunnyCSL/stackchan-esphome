#!/bin/bash
# Flash StackChan via USB (Q6A)
# Usage: ./flash-stackchan.sh [yaml_file] [port]
# Default: stackchan-v12.yaml, /dev/ttyACM0

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
STACKCHAN_DIR="${PROJECT_DIR}/stackchan"
YAML="${1:-stackchan-v12.yaml}"
PORT="${2:-/dev/ttyACM0}"

echo "=== StackChan Flash ==="
echo "YAML: ${STACKCHAN_DIR}/${YAML}"
echo "Port: ${PORT}"

if [ ! -e "${PORT}" ]; then
  echo "ERROR: ${PORT} not found."
  exit 1
fi

~/.venv-llm/bin/esphome run "${STACKCHAN_DIR}/${YAML}" --device "${PORT}"
