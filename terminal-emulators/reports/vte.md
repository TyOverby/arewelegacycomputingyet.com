# VTE Hardcoded Unicode Character Drawing

VTE (Virtual Terminal Emulator) contains hardcoded rendering logic for specific Unicode character classes, bypassing font glyphs entirely and using Cairo graphics primitives to draw pixel-perfect shapes.

## Box Drawing Characters (U+2500–U+257F)

The 128 characters in this range are rendered using 5×5 bitmap patterns.

### Implementation Files

| File | Purpose |
|------|---------|
| [src/box-drawing.hh#L38-L863](https://github.com/GNOME/vte/blob/master/src/box-drawing.hh#L38-L863) | Bitmap definitions for all 128 characters |
| [src/minifont.cc#L1228-L1372](https://github.com/GNOME/vte/blob/master/src/minifont.cc#L1228-L1372) | Main rendering switch statement and bitmap lookup |
| [src/minifont.cc#L1375-L1431](https://github.com/GNOME/vte/blob/master/src/minifont.cc#L1375-L1431) | Dashed line variants |
| [src/minifont.cc#L1433-L1469](https://github.com/GNOME/vte/blob/master/src/minifont.cc#L1433-L1469) | Arc drawing (rounded corners) |
| [src/minifont.cc#L1481-L1483](https://github.com/GNOME/vte/blob/master/src/minifont.cc#L1481-L1483) | Diagonal characters |
| [src/bidi.cc#L730-L770](https://github.com/GNOME/vte/blob/master/src/bidi.cc#L730-L770) | BiDi mirror mapping table |
| [src/vte.cc#L3280-L3301](https://github.com/GNOME/vte/blob/master/src/vte.cc#L3280-L3301) | VT102 line-drawing character mapping |

### How It Works

1. Characters are indexed as `c - 0x2500` (yielding 0–127)
2. Each index maps to a `uint32_t` bitmap in `_vte_draw_box_drawing_bitmaps[128]`
3. The bitmap is scaled and rendered via Cairo

## Symbols for Legacy Computing (U+1FB00–U+1FBDF)

This block contains sextant blocks, octant blocks, diagonal lines, and fill patterns used to recreate legacy computer graphics.

### Implementation Files

All rendering logic is in [src/minifont.cc](https://github.com/GNOME/vte/blob/master/src/minifont.cc):

| Character Range | Lines | Description |
|-----------------|-------|-------------|
| U+1FB00–U+1FB3B | [#L1621-L1687](https://github.com/GNOME/vte/blob/master/src/minifont.cc#L1621-L1687) | Sextant blocks (6-part cell divisions) |
| U+1FB3C–U+1FB67 | [#L1689-L1783](https://github.com/GNOME/vte/blob/master/src/minifont.cc#L1689-L1783) | Segmented diagonal polygons |
| U+1FB68–U+1FB6F | [#L1785-L1807](https://github.com/GNOME/vte/blob/master/src/minifont.cc#L1785-L1807) | Additional sextant characters |
| U+1FB70–U+1FB81 | [#L1809-L1881](https://github.com/GNOME/vte/blob/master/src/minifont.cc#L1809-L1881) | Block characters |
| U+1FB8C–U+1FB94 | [#L1889-L1975](https://github.com/GNOME/vte/blob/master/src/minifont.cc#L1889-L1975) | Transparency-enabled fills (0.5 alpha) |
| U+1FB95–U+1FB99 | [#L1978-L1997](https://github.com/GNOME/vte/blob/master/src/minifont.cc#L1978-L1997) | Pattern fills (checkerboard, diagonal) |
| U+1FB9A–U+1FB9F | [#L1999-L2059](https://github.com/GNOME/vte/blob/master/src/minifont.cc#L1999-L2059) | Smaller block fragments |
| U+1FBA0–U+1FBAE | [#L2061-L2081](https://github.com/GNOME/vte/blob/master/src/minifont.cc#L2061-L2081) | Diagonal box drawings |
| U+1FBBD–U+1FBBF | [#L2084-L2113](https://github.com/GNOME/vte/blob/master/src/minifont.cc#L2084-L2113) | Negative diagonal characters |
| U+1FBD0–U+1FBDF | [#L2424-L2459](https://github.com/GNOME/vte/blob/master/src/minifont.cc#L2424-L2459) | Extended diagonal slopes |
| U+1FBE4–U+1FBE7 | [#L2465-L2483](https://github.com/GNOME/vte/blob/master/src/minifont.cc#L2465-L2483) | Quadrant and octant characters |

### Pattern Data

Fill pattern pixel data is defined at [src/minifont.cc#L215-L253](https://github.com/GNOME/vte/blob/master/src/minifont.cc#L215-L253):

- U+1FB95: Checker board fill
- U+1FB96: Inverse checker board fill
- U+1FB97: Heavy horizontal fill
- U+1FB98: Upper left to lower right fill
- U+1FB99: Upper right to lower left fill

### Helper Functions

| Function | Lines | Purpose |
|----------|-------|---------|
| `sextant()` | [#L667-L701](https://github.com/GNOME/vte/blob/master/src/minifont.cc#L667-L701) | Render 6-cell block characters |
| `octant()` | [#L704-L746](https://github.com/GNOME/vte/blob/master/src/minifont.cc#L704-L746) | Render 8-cell block characters |
| `middle_diagonal()` | Used for diagonal box drawings |
| `diagonal_slope_1_1()` | 1:1 slope diagonal lines |
| `diagonal_slope_2_1()` | 2:1 slope diagonal lines |

### Supporting Files

| File | Purpose |
|------|---------|
| [src/unicode-width.hh#L515](https://github.com/GNOME/vte/blob/master/src/unicode-width.hh#L515) | Width=1 declaration for U+1FB00 block |
| [perf/legacy.py#L29](https://github.com/GNOME/vte/blob/master/perf/legacy.py#L29) | Performance test for sextant rendering |
| [doc/boxes.txt](https://github.com/GNOME/vte/blob/master/doc/boxes.txt) | Visual documentation of box characters |
