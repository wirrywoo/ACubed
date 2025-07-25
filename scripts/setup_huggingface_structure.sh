#!/bin/bash

# Check for at least one argument
if [ "$#" -eq 0 ]; then
  echo "❌ Usage: $0 project1 [project2 ...]"
  exit 1
fi

# Constants
BASE_DIR="huggingface"
TYPES=("datasets" "models")
DATASET_SUBFOLDER=("charts")
MODEL_SUBFOLDER=("difficulty_model")

# Create base and spaces dir
mkdir -p "$BASE_DIR/spaces"

# Loop over each TYPE and user-provided VSRG
for TYPE in "${TYPES[@]}"; do
  if [ "$TYPE" = "datasets" ]; then
    SUBFOLDERS=("${DATASET_SUBFOLDER[@]}")
  elif [ "$TYPE" = "models" ]; then
    SUBFOLDERS=("${MODEL_SUBFOLDER[@]}")
  else
    continue
  fi

  for VSRG in "$@"; do
    for SUB in "${SUBFOLDERS[@]}"; do
      mkdir -p "$BASE_DIR/$TYPE/$VSRG/$SUB"
    done
  done
done
