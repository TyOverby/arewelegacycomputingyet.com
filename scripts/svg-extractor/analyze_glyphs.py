#!/usr/bin/env python3
"""Analyze glyphs in the extracted font and export as SVG paths."""

from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.recordingPen import RecordingPen
import os

FONT_PATH = "extracted_fonts/GNFBED+KreativeSquareUnibook.ttf"


def get_glyph_svg_path(glyph_set, glyph_name):
    """Get the SVG path string for a glyph."""
    pen = SVGPathPen(glyph_set)
    try:
        glyph_set[glyph_name].draw(pen)
        return pen.getCommands()
    except Exception as e:
        return None


def analyze_font():
    """Analyze all glyphs in the font."""
    font = TTFont(FONT_PATH)

    print(f"Font tables: {list(font.keys())}")
    print(f"Units per Em: {font['head'].unitsPerEm}")

    glyph_order = font.getGlyphOrder()
    print(f"\nTotal glyphs: {len(glyph_order)}")
    print(f"Glyph names: {glyph_order[:30]}...")

    # Get glyph set for drawing
    glyph_set = font.getGlyphSet()

    print("\n=== Glyph Analysis ===")
    for i, glyph_name in enumerate(glyph_order[:20]):
        glyph = glyph_set[glyph_name]

        # Get bounding box and width
        width = glyph.width

        # Get SVG path
        svg_path = get_glyph_svg_path(glyph_set, glyph_name)

        print(f"\n{i}. {glyph_name}:")
        print(f"   Width: {width}")
        if svg_path:
            # Truncate long paths
            path_preview = svg_path[:100] + "..." if len(svg_path) > 100 else svg_path
            print(f"   Path: {path_preview}")
        else:
            print("   Path: (empty or error)")

    font.close()


def export_all_glyphs_svg():
    """Export all glyphs as individual SVG files."""
    font = TTFont(FONT_PATH)
    glyph_set = font.getGlyphSet()
    glyph_order = font.getGlyphOrder()
    units_per_em = font['head'].unitsPerEm

    output_dir = "glyph_svgs"
    os.makedirs(output_dir, exist_ok=True)

    print(f"\nExporting {len(glyph_order)} glyphs...")

    for i, glyph_name in enumerate(glyph_order):
        if glyph_name == ".notdef":
            continue

        svg_path = get_glyph_svg_path(glyph_set, glyph_name)
        if not svg_path or svg_path.strip() == "":
            continue

        glyph = glyph_set[glyph_name]
        width = glyph.width

        # Create SVG with proper viewBox
        # Fonts typically have Y going up, SVG has Y going down
        # We'll flip the coordinate system
        svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {units_per_em}">
  <g transform="translate(0, {units_per_em}) scale(1, -1)">
    <path d="{svg_path}" fill="black"/>
  </g>
</svg>'''

        output_path = os.path.join(output_dir, f"{i:03d}_{glyph_name}.svg")
        with open(output_path, "w") as f:
            f.write(svg_content)

    print(f"SVGs saved to {output_dir}/")
    font.close()


if __name__ == "__main__":
    analyze_font()
    export_all_glyphs_svg()
