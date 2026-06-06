#!/bin/bash
# Flash StickS3 via USB (Q6A)
# Usage: ./flash-sticks3.sh [yaml_file]
# Default: sticks3-v11.yaml

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
STICKS3_DIR="${PROJECT_DIR}/sticks3"
YAML="${1:-sticks3-v11.yaml}"
PORT="${2:-/dev/ttyACM0}"

echo "=== StickS3 Flash ==="
echo "YAML: ${STICKS3_DIR}/${YAML}"
echo "Port: ${PORT}"

~/.venv-llm/bin/esphome run "${STICKS3_DIR}/${YAML}" --device "${PORT}"
