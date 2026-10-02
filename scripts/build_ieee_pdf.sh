#!/usr/bin/env bash
# Backwards-compatible entrypoint: accepts project root or configured paper dir.
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
if command -v python3 >/dev/null 2>&1; then
    exec python3 "$SCRIPT_DIR/build_paper.py" "$@"
fi
if command -v python >/dev/null 2>&1; then
    exec python "$SCRIPT_DIR/build_paper.py" "$@"
fi
echo "ERROR: Python 3 is required to build the manuscript." >&2
exit 2
