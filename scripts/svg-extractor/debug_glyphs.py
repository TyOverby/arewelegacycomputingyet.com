#!/usr/bin/env python3
"""Debug glyph structure in the font."""

from fontTools.ttLib import TTFont
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.recordingPen import RecordingPen

FONT_PATH = "extracted_fonts/GNFBED+KreativeSquareUnibook.ttf"


def debug_font():
    font = TTFont(FONT_PATH)

    glyf_table = font["glyf"]
    glyph_order = font.getGlyphOrder()

    print(f"Total glyphs in glyf: {len(glyf_table)}")
    print()

    # Check first few glyphs with actual data
    glyphs_with_data = []
    glyphs_composite = []
    glyphs_empty = []

    for name in glyph_order:
        glyph = glyf_table[name]
        if glyph is None:
            glyphs_empty.append(name)
        elif glyph.isComposite():
            glyphs_composite.append(name)
        elif glyph.numberOfContours > 0:
            glyphs_with_data.append(name)
        else:
            glyphs_empty.append(name)

    print(f"Glyphs with contour data: {len(glyphs_with_data)}")
    print(f"Composite glyphs: {len(glyphs_composite)}")
    print(f"Empty glyphs: {len(glyphs_empty)}")
    print()

    # Show details of first few glyphs with data
    print("=== First 20 glyphs with contour data ===")
    for name in glyphs_with_data[:20]:
        glyph = glyf_table[name]
        print(f"{name}:")
        print(f"  Number of contours: {glyph.numberOfContours}")
        if hasattr(glyph, "xMin"):
            print(f"  Bounds: ({glyph.xMin}, {glyph.yMin}) - ({glyph.xMax}, {glyph.yMax})")
        print()

    # Show composite glyphs
    if glyphs_composite:
        print("=== First 10 composite glyphs ===")
        for name in glyphs_composite[:10]:
            glyph = glyf_table[name]
            print(f"{name}:")
            for component in glyph.components:
                print(f"  Component: {component.glyphName}")
            print()

    font.close()


if __name__ == "__main__":
    debug_font()
