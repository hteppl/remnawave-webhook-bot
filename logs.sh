#!/bin/bash

CONTAINER_NAME="remnawave-webhook-bot"
OUTPUT_DIR="./logs"

TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
OUTPUT_FILE="${OUTPUT_DIR}/${CONTAINER_NAME}-${TIMESTAMP}.log"

mkdir -p "$OUTPUT_DIR"

LOG_PATH=$(docker inspect "$CONTAINER_NAME" --format='{{.LogPath}}')

if [ -z "$LOG_PATH" ]; then
  echo "Container not found: $CONTAINER_NAME"
  exit 1
fi

echo "Container: $CONTAINER_NAME"
echo "Docker log file: $LOG_PATH"
echo "Exporting to: $OUTPUT_FILE"

sudo cp "$LOG_PATH" "$OUTPUT_FILE"
sudo chown "$(whoami)":"$(whoami)" "$OUTPUT_FILE"

echo "Logs exported successfully."
ls -lh "$OUTPUT_FILE"
