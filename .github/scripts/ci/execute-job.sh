#!/bin/bash
# Execute a job with self-healing capabilities
# This script is called by the self-healing workflow

set -e

JOB_NAME="${1:-test}"

echo "Executing job: $JOB_NAME"

case "$JOB_NAME" in
  test)
    echo "Running test suite..."
    if [ -d "tests" ]; then
      pytest tests/ -v || exit 1
    else
      echo "No tests found"
    fi
    ;;
    
  build)
    echo "Building application..."
    if [ -f "Dockerfile" ]; then
      docker build -t test-build . || exit 1
    else
      echo "No Dockerfile found"
    fi
    ;;
    
  lint)
    echo "Running linters..."
    if [ -f "requirements.txt" ]; then
      pip install black flake8 isort
      black --check . || exit 1
      flake8 . || exit 1
      isort --check . || exit 1
    fi
    ;;
    
  *)
    echo "Unknown job: $JOB_NAME"
    exit 1
    ;;
esac

echo "Job $JOB_NAME completed successfully"
exit 0
