#!/usr/bin/env python3
"""Extract embedded fonts from the PDF and save glyph outlines as SVG."""

import os
import fitz  # PyMuPDF
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
import io

PDF_PATH = "../../sources/U1FB00_symbols_for_legacy_computing.pdf"
OUTPUT_DIR = "extracted_fonts"


def extract_fonts():
    """Extract embedded fonts from the PDF."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    doc = fitz.open(PDF_PATH)

    font_list = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        fonts = page.get_fonts()
        for font in fonts:
            xref, ext, type_, name, ref, encoding = font
            if name not in [f[3] for f in font_list]:
                font_list.append(font)
                print(f"Found font: {name} (xref={xref}, type={type_})")

    # Extract fonts - look specifically for the legacy computing font
    for font in font_list:
        xref, ext, type_, name, ref, encoding = font
        if "Kreative" in name or "Square" in name:
            print(f"\nExtracting {name}...")
            try:
                # Get the raw font data
                font_data = doc.extract_font(xref)
                if font_data:
                    # font_data is a tuple: (name, ext, type, content)
                    fname, fext, ftype, content = font_data
                    if content:
                        output_path = os.path.join(OUTPUT_DIR, f"{name}.{fext}")
                        with open(output_path, "wb") as f:
                            f.write(content)
                        print(f"  Saved to {output_path} ({len(content)} bytes)")
            except Exception as e:
                print(f"  Error extracting: {e}")

    doc.close()
    return font_list


def analyze_extracted_font(font_path):
    """Analyze an extracted font and list its glyphs."""
    print(f"\nAnalyzing font: {font_path}")

    try:
        font = TTFont(font_path)
        print(f"Tables: {list(font.keys())}")

        # Get cmap (character map)
        cmap = font.getBestCmap()
        if cmap:
            print(f"\nNumber of mapped characters: {len(cmap)}")

            # Filter for U+1FB00 range
            legacy_chars = {
                cp: name for cp, name in cmap.items() if 0x1FB00 <= cp <= 0x1FBFF
            }
            print(f"Characters in U+1FB00-1FBFF range: {len(legacy_chars)}")

            if legacy_chars:
                print("\nFirst 20 legacy computing characters:")
                for i, (cp, glyph_name) in enumerate(sorted(legacy_chars.items())[:20]):
                    print(f"  U+{cp:04X}: {glyph_name}")

        font.close()
    except Exception as e:
        print(f"Error analyzing font: {e}")


def main():
    print("=== Extracting Fonts from PDF ===\n")
    fonts = extract_fonts()

    # Check for extracted fonts
    if os.path.exists(OUTPUT_DIR):
        for fname in os.listdir(OUTPUT_DIR):
            fpath = os.path.join(OUTPUT_DIR, fname)
            analyze_extracted_font(fpath)


if __name__ == "__main__":
    main()
