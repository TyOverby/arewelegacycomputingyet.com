#!/usr/bin/env python3
"""Check font metrics to determine correct viewBox."""

from fontTools.ttLib import TTFont

FONT_PATH = "extracted_fonts/KreativeSquareUnibook.ttf"


def check_metrics():
    font = TTFont(FONT_PATH)

    # Head table
    head = font["head"]
    print("=== head table ===")
    print(f"  unitsPerEm: {head.unitsPerEm}")
    print(f"  xMin: {head.xMin}")
    print(f"  yMin: {head.yMin}")
    print(f"  xMax: {head.xMax}")
    print(f"  yMax: {head.yMax}")

    # hhea table (horizontal metrics)
    hhea = font["hhea"]
    print("\n=== hhea table ===")
    print(f"  ascent: {hhea.ascent}")
    print(f"  descent: {hhea.descent}")
    print(f"  lineGap: {hhea.lineGap}")
    print(f"  advanceWidthMax: {hhea.advanceWidthMax}")

    # OS/2 table
    os2 = font["OS/2"]
    print("\n=== OS/2 table ===")
    print(f"  sTypoAscender: {os2.sTypoAscender}")
    print(f"  sTypoDescender: {os2.sTypoDescender}")
    print(f"  sTypoLineGap: {os2.sTypoLineGap}")
    print(f"  usWinAscent: {os2.usWinAscent}")
    print(f"  usWinDescent: {os2.usWinDescent}")
    print(f"  xAvgCharWidth: {os2.xAvgCharWidth}")

    # Check actual glyph bounds
    print("\n=== Glyph bounds analysis ===")
    glyf = font["glyf"]
    glyph_set = font.getGlyphSet()

    min_y = float("inf")
    max_y = float("-inf")
    min_x = float("inf")
    max_x = float("-inf")
    widths = set()

    for name in font.getGlyphOrder():
        glyph = glyf.get(name)
        if glyph and hasattr(glyph, "xMin") and glyph.numberOfContours != 0:
            min_x = min(min_x, glyph.xMin)
            max_x = max(max_x, glyph.xMax)
            min_y = min(min_y, glyph.yMin)
            max_y = max(max_y, glyph.yMax)

        # Get advance width
        if name in glyph_set:
            widths.add(glyph_set[name].width)

    print(f"  Global xMin: {min_x}")
    print(f"  Global xMax: {max_x}")
    print(f"  Global yMin: {min_y}")
    print(f"  Global yMax: {max_y}")
    print(f"  Unique widths: {sorted(widths)}")

    # Calculate proper viewBox options
    print("\n=== ViewBox Options ===")

    # Option 1: Use hhea metrics (standard line height)
    width = 720
    ascent = hhea.ascent
    descent = hhea.descent
    height = ascent - descent
    print(f"Option 1 (hhea): viewBox=\"0 {descent} {width} {height}\"")
    print(f"  This gives 720x720 cell with descent at -160")

    # Option 2: Use actual glyph bounds
    actual_height = max_y - min_y
    print(f"\nOption 2 (actual bounds): viewBox=\"{min_x} {min_y} {max_x - min_x} {actual_height}\"")

    # Option 3: Use OS/2 Win metrics
    win_height = os2.usWinAscent + os2.usWinDescent
    print(f"\nOption 3 (OS/2 Win): viewBox=\"0 -{os2.usWinDescent} {width} {win_height}\"")
    print(f"  Ascent: {os2.usWinAscent}, Descent: {os2.usWinDescent}")

    font.close()


if __name__ == "__main__":
    check_metrics()
