#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
bash "$SCRIPT_DIR/run_backend_tests.sh" all
bash "$SCRIPT_DIR/run_worker_tests.sh" all
