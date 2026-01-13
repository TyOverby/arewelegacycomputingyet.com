#!/usr/bin/env python3
"""Check if a font supports the Symbols for Legacy Computing Unicode block."""

import argparse
import sys
from pathlib import Path

from fontTools.ttLib import TTFont

# Symbols for Legacy Computing block: U+1FB00 to U+1FBFA
LEGACY_COMPUTING_START = 0x1FB00
LEGACY_COMPUTING_END = 0x1FBFA


def has_glyph(font: TTFont, codepoint: int) -> bool:
    """Check if a font has a glyph for the given codepoint."""
    for table in font["cmap"].tables:
        if codepoint in table.cmap:
            return True
    return False


def main():
    parser = argparse.ArgumentParser(
        description="Check if a font supports the Symbols for Legacy Computing Unicode block (U+1FB00-U+1FBFA)"
    )
    parser.add_argument("font", type=Path, help="Path to the font file (.ttf, .otf)")
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="Only output summary and exit code"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Show status for each codepoint"
    )
    args = parser.parse_args()

    if not args.font.exists():
        print(f"Error: Font file not found: {args.font}", file=sys.stderr)
        sys.exit(2)

    try:
        font = TTFont(args.font)
    except Exception as e:
        print(f"Error: Could not load font: {e}", file=sys.stderr)
        sys.exit(2)

    supported = 0
    missing = 0
    total = LEGACY_COMPUTING_END - LEGACY_COMPUTING_START + 1

    for codepoint in range(LEGACY_COMPUTING_START, LEGACY_COMPUTING_END + 1):
        has_it = has_glyph(font, codepoint)
        if has_it:
            supported += 1
        else:
            missing += 1

        if args.verbose:
            char = chr(codepoint)
            status = "✓" if has_it else "✗"
            print(f"{status} U+{codepoint:05X} ({char})")

    if not args.quiet:
        print(f"\nSymbols for Legacy Computing (U+1FB00-U+1FBFA)")
        print(f"Supported: {supported}/{total} ({100*supported/total:.1f}%)")
        if missing > 0:
            print(f"Missing:   {missing}")

    sys.exit(0 if missing == 0 else 1)


if __name__ == "__main__":
    main()
