# CLAUDE.md

## Project Overview

**arewelegacycomputingyet.com** is a research project investigating support for Unicode's "Symbols for Legacy Computing" (U+1FB00-U+1FBFF) and its supplement block (U+1CC00-U+1CEBF) in modern terminal emulators and fonts.

The project name follows the "Are we X yet?" meme format, asking whether modern systems properly support these legacy computing symbols which include sextant blocks, block mosaics, diagonal lines, 7-segment digits, and retro game sprites.

## Repository Structure

```
├── font-codepoint-checker/     # Python tool for checking font glyph support
│   ├── font_codepoint_checker.py  # Main utility
│   ├── check_fonts.sh          # Test multiple fonts
│   └── pyproject.toml          # Python project config (uses uv)
├── terminal-emulators/reports/ # Analysis of terminal emulator implementations
│   ├── alacritty.md           # Rust-based, procedural glyph drawing
│   ├── ghostty.md             # Zig-based, sprite font system
│   ├── kitty.md               # C-based, box font with 4x supersampling
│   ├── vte.md                 # C/Cairo, 5×5 bitmap patterns
│   └── xterm-js.md            # TypeScript/WebGL, SVG paths
├── sources/                    # Unicode specification PDFs
└── tests/                      # Visual test scripts and output
    ├── legacy_computing_table.sh           # U+1FB00 block table
    └── legacy_computing_supplement_table.sh # U+1CC00 block table
```

## Technologies

- **Shell/Bash** - Test scripts for rendering character tables
- **Python 3.11+** - Font checking tool (uses `fonttools` library)
- **uv** - Python package manager

## Common Commands

```bash
# Run the legacy computing table test (displays 16x16 Unicode table)
bash tests/legacy_computing_table.sh

# Run the supplement table test
bash tests/legacy_computing_supplement_table.sh

# Check font support for legacy computing symbols
cd font-codepoint-checker
bash check_fonts.sh

# Or check a specific font
uv run python font_codepoint_checker.py /path/to/font.ttf
```

## Unicode Ranges of Interest

- **U+1FB00-U+1FBFA** - Symbols for Legacy Computing (main block)
- **U+1CC00-U+1CEBF** - Symbols for Legacy Computing Supplement
- **U+2500-U+259F** - Box Drawing and Block Elements (related)

## Key Concepts

- **Sextants**: 6-part cell divisions (2×3 grid)
- **Octants**: 8-part cell divisions (2×4 grid)
- **Smooth Mosaics**: Block elements with curved edges
- **Procedural Rendering**: Terminal emulators often bypass fonts and draw these symbols directly using geometric primitives
