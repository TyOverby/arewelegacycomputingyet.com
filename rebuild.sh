#!/bin/bash
# Watch for file changes and regenerate index.html

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GENERATE_SCRIPT="$SCRIPT_DIR/scripts/template/generate.py"

# Check if inotifywait is available
if ! command -v inotifywait &> /dev/null; then
    echo "Error: inotifywait not found. Install with: sudo apt install inotify-tools"
    exit 1
fi

# Initial build
echo "Running initial build..."
python3 "$GENERATE_SCRIPT"

echo "Watching for changes... (Ctrl+C to stop)"

# Watch for changes in relevant directories
inotifywait -m -r -e modify,create,delete \
    --exclude '(\.git|__pycache__|\.pyc|index\.html)' \
    "$SCRIPT_DIR/scripts/template" \
    "$SCRIPT_DIR/terminal-emulators" \
    "$SCRIPT_DIR/svgs" \
    2>/dev/null | while read -r directory events filename; do
    echo "Change detected: $directory$filename ($events)"
    echo "Regenerating index.html..."
    python3 "$GENERATE_SCRIPT"
    echo "Done."
done
