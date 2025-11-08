#!/usr/bin/env bash
set -e
export GITTODOC_ROOT="${GITTODOC_ROOT:-$(pwd)}"
export GITTODOC_CACHE="${GITTODOC_CACHE:-$(pwd)}"
uvicorn main:app --host 0.0.0.0 --port 8099
