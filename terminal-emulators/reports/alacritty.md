# Alacritty: Hardcoded Unicode Character Rendering

Alacritty includes a built-in font renderer that bypasses normal font rendering for specific Unicode character ranges. This ensures pixel-perfect alignment of box drawing and block characters regardless of the installed system fonts.

## Primary Implementation

All hardcoded character rendering logic lives in:

**[`alacritty/src/renderer/text/builtin_font.rs`](https://github.com/alacritty/alacritty/blob/master/alacritty/src/renderer/text/builtin_font.rs)**

The main dispatch function [`builtin_glyph()`](https://github.com/alacritty/alacritty/blob/master/alacritty/src/renderer/text/builtin_font.rs#L23-L47) checks if a character falls into the supported ranges and routes to the appropriate drawing function.

## Box Drawing Characters (U+2500 - U+259F)

| Range | Description | Source |
|-------|-------------|--------|
| U+2500-U+2503 | Horizontal and vertical lines | [L160](https://github.com/alacritty/alacritty/blob/master/alacritty/src/renderer/text/builtin_font.rs#L160) |
| U+2504-U+2505, U+2508-U+2509, U+254C-U+254D | Horizontal dashes | [L112-L131](https://github.com/alacritty/alacritty/blob/master/alacritty/src/renderer/text/builtin_font.rs#L112-L131) |
| U+2506-U+2507, U+250A-U+250B, U+254E-U+254F | Vertical dashes | [L133-L152](https://github.com/alacritty/alacritty/blob/master/alacritty/src/renderer/text/builtin_font.rs#L133-L152) |
| U+250C-U+254B | Light and heavy box components | [L160](https://github.com/alacritty/alacritty/blob/master/alacritty/src/renderer/text/builtin_font.rs#L160) |
| U+2550-U+256C | Double line box components | [L247-L349](https://github.com/alacritty/alacritty/blob/master/alacritty/src/renderer/text/builtin_font.rs#L247-L349) |
| U+256D-U+2570 | Rounded corners (╭╮╯╰) | [L351-L393](https://github.com/alacritty/alacritty/blob/master/alacritty/src/renderer/text/builtin_font.rs#L351-L393) |
| U+2571-U+2573 | Diagonal lines (╱╲╳) | [L61-L106](https://github.com/alacritty/alacritty/blob/master/alacritty/src/renderer/text/builtin_font.rs#L61-L106) |
| U+2574-U+257F | Mixed light/heavy line segments | [L160](https://github.com/alacritty/alacritty/blob/master/alacritty/src/renderer/text/builtin_font.rs#L160) |
| U+2580-U+2590, U+2594-U+2595 | Block elements (halves, eighths) | [L396-L449](https://github.com/alacritty/alacritty/blob/master/alacritty/src/renderer/text/builtin_font.rs#L396-L449) |
| U+2588, U+2591-U+2593 | Full block and shades | [L451-L460](https://github.com/alacritty/alacritty/blob/master/alacritty/src/renderer/text/builtin_font.rs#L451-L460) |
| U+2596-U+259F | Quadrants | [L462-L499](https://github.com/alacritty/alacritty/blob/master/alacritty/src/renderer/text/builtin_font.rs#L462-L499) |

## Symbols for Legacy Computing (U+1FB00 range)

| Range | Description | Source |
|-------|-------------|--------|
| U+1FB00-U+1FB3B | Sextants (6-part block characters) | [L504-L582](https://github.com/alacritty/alacritty/blob/master/alacritty/src/renderer/text/builtin_font.rs#L504-L582) |
| U+1FB82-U+1FB8B | Legacy computing block elements | [L400](https://github.com/alacritty/alacritty/blob/master/alacritty/src/renderer/text/builtin_font.rs#L400), [L426-L430](https://github.com/alacritty/alacritty/blob/master/alacritty/src/renderer/text/builtin_font.rs#L426-L430), [L444](https://github.com/alacritty/alacritty/blob/master/alacritty/src/renderer/text/builtin_font.rs#L444) |

## Powerline Symbols (U+E0B0 range)

| Range | Description | Source |
|-------|-------------|--------|
| U+E0B0-U+E0B3 | Powerline triangles and arrows | [L17-L20](https://github.com/alacritty/alacritty/blob/master/alacritty/src/renderer/text/builtin_font.rs#L17-L20), [L599-L670](https://github.com/alacritty/alacritty/blob/master/alacritty/src/renderer/text/builtin_font.rs#L599-L670) |

## Configuration

The built-in font rendering is **enabled by default** and controlled by the `builtin_box_drawing` configuration option:

- **Definition**: [`alacritty/src/config/font.rs#L43-L44`](https://github.com/alacritty/alacritty/blob/master/alacritty/src/config/font.rs#L43-L44)
- **Default value**: `true` ([`font.rs#L82`](https://github.com/alacritty/alacritty/blob/master/alacritty/src/config/font.rs#L82))
- **Cache integration**: [`glyph_cache.rs#L77-L78`](https://github.com/alacritty/alacritty/blob/master/alacritty/src/renderer/text/glyph_cache.rs#L77-L78), [`glyph_cache.rs#L212-L221`](https://github.com/alacritty/alacritty/blob/master/alacritty/src/renderer/text/glyph_cache.rs#L212-L221)

## Implementation Details

### Rendering Pipeline

The custom renderer uses a `Canvas` struct ([L708-L974](https://github.com/alacritty/alacritty/blob/master/alacritty/src/renderer/text/builtin_font.rs#L708-L974)) that provides:

- RGB bitmap buffer rasterization
- Anti-aliased line drawing using Xiaolin Wu's algorithm ([L817-L885](https://github.com/alacritty/alacritty/blob/master/alacritty/src/renderer/text/builtin_font.rs#L817-L885))
- Primitives for rectangles, circles (for rounded corners), and fills

### Character-Specific Techniques

- **Diagonal lines**: Extended canvas with double stroke for proper anti-aliasing
- **Dashed lines**: Calculated gaps and dash lengths based on cell dimensions
- **Double lines**: Careful positioning to handle overlapping line segments
- **Rounded corners**: Circular distance calculations with axis mirroring
- **Block fills**: Fractional fills (1/8 increments for blocks, 1/3 for sextants)
- **Shades**: Predefined alpha levels (64, 128, 192 gray values)

## Test Coverage

Comprehensive tests ensure all character ranges are covered:
[`builtin_font.rs#L1003-L1031`](https://github.com/alacritty/alacritty/blob/master/alacritty/src/renderer/text/builtin_font.rs#L1003-L1031)
