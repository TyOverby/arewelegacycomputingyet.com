#!/bin/bash
# Check several common fonts for Symbols for Legacy Computing support

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

FONTS=(
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
    "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf"
    "/usr/share/fonts/truetype/noto/NotoSansSymbols2-Regular.ttf"
    "/usr/share/fonts/truetype/noto/NotoSansSymbols-Regular.ttf"
    "/usr/share/fonts/truetype/noto/NotoSansMono-Regular.ttf"
    "/usr/share/fonts/opentype/urw-base35/URWGothic-DemiOblique.otf"
)

for font in "${FONTS[@]}"; do
    if [[ -f "$font" ]]; then
        echo "=== $(basename "$font") ==="
        uv run --project "$SCRIPT_DIR" python font_codepoint_checker.py "$font"
        echo
    else
        echo "=== $(basename "$font") ==="
        echo "  (not installed)"
        echo
    fi
done
