# Kitty Terminal: Hardcoded Unicode Character Rendering

Kitty has extensive hardcoded rendering logic for special Unicode characters, bypassing system fonts to ensure pixel-perfect, consistent display.

## Box Drawing Characters (U+2500)

### Font Selection

In [`kitty/fonts.c`](https://github.com/kovidgoyal/kitty/blob/master/kitty/fonts.c#L733-L744), the `font_for_cell()` function identifies box drawing characters and routes them to the internal BOX_FONT renderer:

```c
case 0x2500 ... 0x2573:    // Light box drawings
case 0x2574 ... 0x259f:    // Additional box drawings
case 0x25d6 ... 0x25d7:    // Circle segments
case 0x25cb: case 0x25c9: case 0x25cf:  // Circles
case 0x25dc ... 0x25e5:    // Geometric shapes
case 0x2800 ... 0x28ff:    // Braille patterns
```

Glyph ID assignment for caching occurs in [`box_glyph_id()`](https://github.com/kovidgoyal/kitty/blob/master/kitty/fonts.c#L772-L793).

### Rendering Implementation

The main rendering logic lives in [`kitty/decorations.c`](https://github.com/kovidgoyal/kitty/blob/master/kitty/decorations.c):

| Function | Lines | Description |
|----------|-------|-------------|
| `render_box_char()` | [1538-1916](https://github.com/kovidgoyal/kitty/blob/master/kitty/decorations.c#L1538-L1916) | Main switch statement handling hundreds of individual characters |
| `braille()` / `braille_dot()` | [1481-1508](https://github.com/kovidgoyal/kitty/blob/master/kitty/decorations.c#L1481-L1508) | Braille pattern rendering (U+2800-U+28FF) |

#### Supported Character Types

- Light and heavy lines (─, ━, │, ┃)
- Dashed/dotted lines (┄, ┅, ┆, ┇, ┈, ┉, ┊, ┋)
- Corners and intersections (┌, ┐, └, ┘, ├, ┤, ┬, ┴, ┼)
- Double-line characters (═, ║, ╒, ╕, ╘, ╛)
- Rounded corners (╭, ╮, ╰, ╯)
- Block elements (█, ▀, ▁, ▂, ▃)
- Shade patterns (░, ▒, ▓)
- Braille patterns (⠀-⣿)

---

## Symbols for Legacy Computing (U+1FB00)

### Font Selection

In [`kitty/fonts.c`](https://github.com/kovidgoyal/kitty/blob/master/kitty/fonts.c#L741-L742):

```c
case 0x1fb00 ... 0x1fbae:  // symbols for legacy computing
```

Glyph IDs are mapped in [`box_glyph_id()`](https://github.com/kovidgoyal/kitty/blob/master/kitty/fonts.c#L782-L783):

```c
case 0x1fb00 ... 0x1fbae:
    return 0x1000 + ch - 0x1fb00;
```

### Rendering Implementation

Sextant rendering in [`kitty/decorations.c`](https://github.com/kovidgoyal/kitty/blob/master/kitty/decorations.c):

| Function | Lines | Description |
|----------|-------|-------------|
| `draw_sextant()` | [1511-1527](https://github.com/kovidgoyal/kitty/blob/master/kitty/decorations.c#L1511-L1527) | Draws individual sextant sections (2x3 grid) |
| `sextant()` | [1529-1535](https://github.com/kovidgoyal/kitty/blob/master/kitty/decorations.c#L1529-L1535) | Orchestrates which sections to fill using bit operations |

Character mapping in `render_box_char()` at [lines 1897-1899](https://github.com/kovidgoyal/kitty/blob/master/kitty/decorations.c#L1897-L1899):

```c
case 0x1fb00 ... 0x1fb00 + 19: sextant(c, ch - 0x1fb00 + 1); break;
case 0x1fb14 ... 0x1fb14 + 19: sextant(c, ch - 0x1fb00 + 2); break;
case 0x1fb28 ... 0x1fb28 + 19: sextant(c, ch - 0x1fb00 + 3); break;
```

---

## Additional Hardcoded Ranges

Kitty also renders these character ranges programmatically:

| Range | Description | Location |
|-------|-------------|----------|
| U+1CD00-U+1CDE5 | Octants (4x2 grid) | [decorations.c:969-1026](https://github.com/kovidgoyal/kitty/blob/master/kitty/decorations.c#L969-L1026) |
| U+E0B0-U+E0BF | Powerline symbols | [fonts.c:738](https://github.com/kovidgoyal/kitty/blob/master/kitty/fonts.c#L738) |
| U+EE00-U+EE0B | Fira Code progress bars | [fonts.c:739](https://github.com/kovidgoyal/kitty/blob/master/kitty/fonts.c#L739) |
| U+F5D0-U+F60D | Branch drawing characters | [fonts.c:743](https://github.com/kovidgoyal/kitty/blob/master/kitty/fonts.c#L743) |

---

## Implementation Details

- **Supersampling**: Uses 4x oversample factor (`SUPERSAMPLE_FACTOR`) for antialiasing
- **Canvas-based rendering**: Draws geometric primitives (lines, rectangles, fills) to alpha masks
- **Configurable**: Can be disabled via `allow_use_of_box_fonts` flag to use system fonts instead
- **Header declaration**: [`kitty/decorations.h:26`](https://github.com/kovidgoyal/kitty/blob/master/kitty/decorations.h#L26)
- **Tests**: [`kitty_tests/fonts.py:299-305`](https://github.com/kovidgoyal/kitty/blob/master/kitty_tests/fonts.py#L299-L305)
