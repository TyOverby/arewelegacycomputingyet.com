# Ghostty: Hardcoded Unicode Character Rendering

Ghostty procedurally generates glyphs for certain Unicode character classes rather than relying on font fallbacks. This document describes the two main classes: Box Drawing and Symbols for Legacy Computing.

## Box Drawing Characters (U+2500-U+257F)

All 128 box drawing characters are rendered procedurally via the sprite font system.

### Primary Implementation

**[src/font/sprite/draw/box.zig](https://github.com/ghostty-org/ghostty/blob/main/src/font/sprite/draw/box.zig)**

| Function | Lines | Description |
|----------|-------|-------------|
| `draw2500_257F` | [48-397](https://github.com/ghostty-org/ghostty/blob/main/src/font/sprite/draw/box.zig#L48-L397) | Main dispatch for all box drawing characters |
| `linesChar` | [399-636](https://github.com/ghostty-org/ghostty/blob/main/src/font/sprite/draw/box.zig#L399-L636) | Renders intersection-style characters (┼, ├, etc.) |
| `arc` | [694-777](https://github.com/ghostty-org/ghostty/blob/main/src/font/sprite/draw/box.zig#L694-L777) | Rounded corners (╭ ╮ ╯ ╰) |
| `dashHorizontal` | [779-851](https://github.com/ghostty-org/ghostty/blob/main/src/font/sprite/draw/box.zig#L779-L851) | Dashed horizontal lines (┄ ┅ ┈ ┉) |
| `dashVertical` | [853-929](https://github.com/ghostty-org/ghostty/blob/main/src/font/sprite/draw/box.zig#L853-L929) | Dashed vertical lines (┆ ┇ ┊ ┋) |
| `lightDiagonalUpperRightToLowerLeft` | [638-660](https://github.com/ghostty-org/ghostty/blob/main/src/font/sprite/draw/box.zig#L638-L660) | Diagonal slash (╱) |
| `lightDiagonalUpperLeftToLowerRight` | [662-684](https://github.com/ghostty-org/ghostty/blob/main/src/font/sprite/draw/box.zig#L662-L684) | Diagonal backslash (╲) |
| `lightDiagonalCross` | [686-692](https://github.com/ghostty-org/ghostty/blob/main/src/font/sprite/draw/box.zig#L686-L692) | Diagonal cross (╳) |

### Data Model

The [`Lines` packed struct](https://github.com/ghostty-org/ghostty/blob/main/src/font/sprite/draw/box.zig#L34-L46) encodes line style (none/light/heavy/double) for each of four directions from the cell center.

### Related Files

- **[src/font/sprite/draw/block.zig](https://github.com/ghostty-org/ghostty/blob/main/src/font/sprite/draw/block.zig)** - Block elements (U+2580-U+259F)
- **[src/renderer/cell.zig#L323-L329](https://github.com/ghostty-org/ghostty/blob/main/src/renderer/cell.zig#L323-L329)** - `isBoxDrawing()` classification

---

## Symbols for Legacy Computing (U+1FB00-U+1FBFF)

The entire "Symbols for Legacy Computing" block is rendered procedurally.

### Primary Implementation

**[src/font/sprite/draw/symbols_for_legacy_computing.zig](https://github.com/ghostty-org/ghostty/blob/main/src/font/sprite/draw/symbols_for_legacy_computing.zig)**

| Function | Lines | Description |
|----------|-------|-------------|
| `draw1FB00_1FB3B` | [97-127](https://github.com/ghostty-org/ghostty/blob/main/src/font/sprite/draw/symbols_for_legacy_computing.zig#L97-L127) | Sextants |
| `draw1FB3C_1FB67` | [130-483](https://github.com/ghostty-org/ghostty/blob/main/src/font/sprite/draw/symbols_for_legacy_computing.zig#L130-L483) | Smooth mosaics (hand-written lookup table) |
| `draw1FB68_1FB6F` | [485-547](https://github.com/ghostty-org/ghostty/blob/main/src/font/sprite/draw/symbols_for_legacy_computing.zig#L485-L547) | Edge triangles |
| `draw1FB70_1FB75` | [550-571](https://github.com/ghostty-org/ghostty/blob/main/src/font/sprite/draw/symbols_for_legacy_computing.zig#L550-L571) | Vertical one-eighth blocks |
| `draw1FB76_1FB7B` | [573-593](https://github.com/ghostty-org/ghostty/blob/main/src/font/sprite/draw/symbols_for_legacy_computing.zig#L573-L593) | Horizontal one-eighth blocks |
| `draw1FB7C_1FB97` | [595-718](https://github.com/ghostty-org/ghostty/blob/main/src/font/sprite/draw/symbols_for_legacy_computing.zig#L595-L718) | Complex block combinations |
| `draw1FB98` | [722-758](https://github.com/ghostty-org/ghostty/blob/main/src/font/sprite/draw/symbols_for_legacy_computing.zig#L722-L758) | Upper left to lower right fill |
| `draw1FB99` | [762-798](https://github.com/ghostty-org/ghostty/blob/main/src/font/sprite/draw/symbols_for_legacy_computing.zig#L762-L798) | Upper right to lower left fill |
| `draw1FB9A_1FB9F` | [800-832](https://github.com/ghostty-org/ghostty/blob/main/src/font/sprite/draw/symbols_for_legacy_computing.zig#L800-L832) | Edge and corner triangles |
| `draw1FBA0_1FBAE` | [834-878](https://github.com/ghostty-org/ghostty/blob/main/src/font/sprite/draw/symbols_for_legacy_computing.zig#L834-L878) | Corner diagonal lines |
| `draw1FBD0_1FBDF` | [999-1189](https://github.com/ghostty-org/ghostty/blob/main/src/font/sprite/draw/symbols_for_legacy_computing.zig#L999-L1189) | Cell diagonals |
| `draw1FBE0_1FBEF` | [1191-1237](https://github.com/ghostty-org/ghostty/blob/main/src/font/sprite/draw/symbols_for_legacy_computing.zig#L1191-L1237) | Circle elements |

### Unicode 16.0 Supplement (U+1CC00-U+1CEBF)

**[src/font/sprite/draw/symbols_for_legacy_computing_supplement.zig](https://github.com/ghostty-org/ghostty/blob/main/src/font/sprite/draw/symbols_for_legacy_computing_supplement.zig)**

| Function | Lines | Description |
|----------|-------|-------------|
| `draw1CD00_1CDE5` | [70-132](https://github.com/ghostty-org/ghostty/blob/main/src/font/sprite/draw/symbols_for_legacy_computing_supplement.zig#L70-L132) | Octants |
| `draw1CC21_1CC2F` | [136-191](https://github.com/ghostty-org/ghostty/blob/main/src/font/sprite/draw/symbols_for_legacy_computing_supplement.zig#L136-L191) | Separated block quadrants |
| `draw1CC30_1CC3F` | [203-245](https://github.com/ghostty-org/ghostty/blob/main/src/font/sprite/draw/symbols_for_legacy_computing_supplement.zig#L203-L245) | Twelfth and quarter circle pieces |
| `draw1CE51_1CE8F` | [379-456](https://github.com/ghostty-org/ghostty/blob/main/src/font/sprite/draw/symbols_for_legacy_computing_supplement.zig#L379-L456) | Separated block sextants |
| `draw1CE90_1CEAF` | [459-538](https://github.com/ghostty-org/ghostty/blob/main/src/font/sprite/draw/symbols_for_legacy_computing_supplement.zig#L459-L538) | Sixteenth blocks |

### Classification

**[src/renderer/cell.zig#L339-L347](https://github.com/ghostty-org/ghostty/blob/main/src/renderer/cell.zig#L339-L347)** - `isLegacyComputing()` identifies codepoints in both ranges.

---

## Sprite Font Architecture

The sprite font system automatically discovers and dispatches to drawing functions.

### Key Files

| File | Description |
|------|-------------|
| [src/font/sprite/Face.zig](https://github.com/ghostty-org/ghostty/blob/main/src/font/sprite/Face.zig) | Sprite font face with compile-time range discovery |
| [src/font/sprite/Face.zig#L57-L145](https://github.com/ghostty-org/ghostty/blob/main/src/font/sprite/Face.zig#L57-L145) | Automatic collection of `draw*` functions into lookup ranges |
| [src/font/sprite/Face.zig#L147-L162](https://github.com/ghostty-org/ghostty/blob/main/src/font/sprite/Face.zig#L147-L162) | `getDrawFn()` - dispatch to appropriate drawing function |
| [src/font/sprite/Face.zig#L165-L171](https://github.com/ghostty-org/ghostty/blob/main/src/font/sprite/Face.zig#L165-L171) | `hasCodepoint()` - check if sprite can render a codepoint |
| [src/font/CodepointResolver.zig#L139-L145](https://github.com/ghostty-org/ghostty/blob/main/src/font/CodepointResolver.zig#L139-L145) | Integration with font fallback system |
| [src/font/sprite/draw/common.zig](https://github.com/ghostty-org/ghostty/blob/main/src/font/sprite/draw/common.zig) | Shared utilities (thickness, line drawing helpers) |
| [src/font/Metrics.zig#L30](https://github.com/ghostty-org/ghostty/blob/main/src/font/Metrics.zig#L30) | `box_thickness` metric controlling stroke width |

### How It Works

1. Functions named `draw<MIN>_<MAX>` or `draw<CODEPOINT>` are collected at compile time
2. Ranges are validated for no overlap
3. `CodepointResolver` checks `sprite.hasCodepoint()` before font fallback
4. Glyphs are rendered procedurally into the font atlas on demand
