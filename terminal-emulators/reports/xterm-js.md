# xterm.js Custom Unicode Character Rendering

xterm.js includes extensive hardcoded logic for rendering specific Unicode character classes using vector graphics rather than bitmap fonts.

## Primary Implementation

**[`addons/addon-webgl/src/customGlyphs/CustomGlyphDefinitions.ts`](https://github.com/xtermjs/xterm.js/blob/master/addons/addon-webgl/src/customGlyphs/CustomGlyphDefinitions.ts)** (~997 lines)

This file contains all custom glyph definitions for both character classes.

---

## Box Drawing Characters (U+2500-U+259F)

**Range:** 160 characters

### Detection

[`src/browser/renderer/shared/RendererUtils.ts#L30-L32`](https://github.com/xtermjs/xterm.js/blob/master/src/browser/renderer/shared/RendererUtils.ts#L30-L32)

```typescript
function isBoxOrBlockGlyph(codepoint: number): boolean {
  return 0x2500 <= codepoint && codepoint <= 0x259F;
}
```

### Definitions

| Range | Description | Source |
|-------|-------------|--------|
| U+2500-U+257F | Box drawing (lines, corners, intersections) | [Lines 37-189](https://github.com/xtermjs/xterm.js/blob/master/addons/addon-webgl/src/customGlyphs/CustomGlyphDefinitions.ts#L37-L189) |
| U+2580-U+259F | Block elements | [Lines 191-244](https://github.com/xtermjs/xterm.js/blob/master/addons/addon-webgl/src/customGlyphs/CustomGlyphDefinitions.ts#L191-L244) |

### Rendering Strategies

1. **SVG Path Functions** - Characters defined as path commands (e.g., `'M0,.5 L1,.5'` for horizontal line)
2. **Octant Block Vectors** - Block elements use 8x8 grid coordinates
3. **Block Patterns** - Shaded blocks (░▒▓) use 2x2 repeating patterns

### Reusable Shape Constants

[Lines 970-997](https://github.com/xtermjs/xterm.js/blob/master/addons/addon-webgl/src/customGlyphs/CustomGlyphDefinitions.ts#L970-L997)

```typescript
LEFT_TO_RIGHT = 'M0,.5 L1,.5'        // ─
TOP_TO_BOTTOM = 'M.5,0 L.5,1'        // │
CROSS = 'M0,.5 L1,.5 M.5,0 L.5,1'    // ┼
```

---

## Symbols for Legacy Computing (U+1FB00-U+1FBF9)

### Definitions

| Range | Description | Source |
|-------|-------------|--------|
| U+1FB00-U+1FB3B | Sextant blocks (2x3 grid patterns) | [Lines 430-495](https://github.com/xtermjs/xterm.js/blob/master/addons/addon-webgl/src/customGlyphs/CustomGlyphDefinitions.ts#L430-L495) |
| U+1FB3C-U+1FB6F | Smooth mosaic / diagonal blocks | [Lines 497-549](https://github.com/xtermjs/xterm.js/blob/master/addons/addon-webgl/src/customGlyphs/CustomGlyphDefinitions.ts#L497-L549) |
| U+1FB70-U+1FB8B | Vertical/horizontal bars | [Lines 551-600](https://github.com/xtermjs/xterm.js/blob/master/addons/addon-webgl/src/customGlyphs/CustomGlyphDefinitions.ts#L551-L600) |
| U+1FB8C-U+1FB9F | Rectangular/triangular shades | [Lines 602-680](https://github.com/xtermjs/xterm.js/blob/master/addons/addon-webgl/src/customGlyphs/CustomGlyphDefinitions.ts#L602-L680) |
| U+1FBA0-U+1FBAE | Character cell diagonals | [Lines 682-720](https://github.com/xtermjs/xterm.js/blob/master/addons/addon-webgl/src/customGlyphs/CustomGlyphDefinitions.ts#L682-L720) |
| U+1FBB0-U+1FBCA | Terminal graphics (icons, figures) | [Lines 722-820](https://github.com/xtermjs/xterm.js/blob/master/addons/addon-webgl/src/customGlyphs/CustomGlyphDefinitions.ts#L722-L820) |
| U+1FBF0-U+1FBF9 | 7-segment display digits | [Lines 410-428](https://github.com/xtermjs/xterm.js/blob/master/addons/addon-webgl/src/customGlyphs/CustomGlyphDefinitions.ts#L410-L428) |

### Helper Functions

**Sextant Generator** - [Lines 829-857](https://github.com/xtermjs/xterm.js/blob/master/addons/addon-webgl/src/customGlyphs/CustomGlyphDefinitions.ts#L829-L857)

Generates 2x3 grid patterns from 6-bit masks. Divides cell into 2 columns x 3 rows with heights 3/8, 2/8, 3/8.

**Segmented Digit Generator** - [Lines 882-960](https://github.com/xtermjs/xterm.js/blob/master/addons/addon-webgl/src/customGlyphs/CustomGlyphDefinitions.ts#L882-L960)

Renders LED-style 7-segment numerals.

---

## Supporting Files

| File | Purpose |
|------|---------|
| [`src/common/data/Charsets.ts#L30-L62`](https://github.com/xtermjs/xterm.js/blob/master/src/common/data/Charsets.ts#L30-L62) | VT100 DEC character set mappings |
| [`addons/addon-webgl/src/customGlyphs/CustomGlyphRasterizer.ts#L10-L38`](https://github.com/xtermjs/xterm.js/blob/master/addons/addon-webgl/src/customGlyphs/CustomGlyphRasterizer.ts#L10-L38) | Converts definitions to rasterized glyphs |
| [`addons/addon-webgl/src/customGlyphs/Types.ts`](https://github.com/xtermjs/xterm.js/blob/master/addons/addon-webgl/src/customGlyphs/Types.ts) | Type definitions for custom glyph system |
| [`addons/addon-webgl/src/TextureAtlas.ts`](https://github.com/xtermjs/xterm.js/blob/master/addons/addon-webgl/src/TextureAtlas.ts) | Integrates custom glyphs into WebGL texture atlas |

---

## Architecture

1. **Detection** - `isBoxOrBlockGlyph()` identifies characters needing custom rendering
2. **Definition Lookup** - `customGlyphDefinitions` object maps codepoints to rendering instructions
3. **Rasterization** - `tryDrawCustomGlyph()` dispatches to appropriate drawing function based on type
4. **Caching** - Rendered glyphs cached in `TextureAtlas` for efficient WebGL rendering

### Rendering Types

- `PATH_FUNCTION` - SVG-like paths with variable parameters
- `PATH` - Static SVG path strings
- `SOLID_OCTANT_BLOCK_VECTOR` - 8x8 grid-based blocks
- `BLOCK_PATTERN` - Repeating 2x2 patterns with optional clip paths
- `VECTOR_SHAPE` - Full vector shapes with stroke/fill
- `BRAILLE` - Specialized dot-pattern rendering
