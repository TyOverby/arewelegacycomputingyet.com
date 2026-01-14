#!/usr/bin/env python3
"""Generate SVG files for Legacy Computing symbols from PDF font data."""

import os
import re
import fitz
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

# Configuration for each Unicode block
BLOCKS = {
    "legacy_computing": {
        "pdf_path": "../../sources/U1FB00_symbols_for_legacy_computing.pdf",
        "output_dir": "../../svgs/legacy_computing",
        "range_start": 0x1FB00,
        "range_end": 0x1FBFF,
        "font_name_pattern": "Kreative",
        "title": "Symbols for Legacy Computing",
        # Single section covering the whole range
        "sections": [
            {"start": 0x1FB00, "end": 0x1FBFF, "title": "Symbols for Legacy Computing", "range_label": "1FB00 - 1FBFF"},
        ],
    },
    "legacy_computing_supplement": {
        "pdf_path": "../../sources/U1CC00_symbols_for_legacy_computing_supplement.pdf",
        "output_dir": "../../svgs/legacy_computing_supplement",
        "range_start": 0x1CC00,
        "range_end": 0x1CEBF,
        "font_name_pattern": "Kreative",
        "title": "Symbols for Legacy Computing Supplement",
        # Three sections matching the PDF layout
        "sections": [
            {"start": 0x1CC00, "end": 0x1CCEF, "title": "Symbols for Legacy Computing Supplement", "range_label": "1CC00 - 1CCEF"},
            {"start": 0x1CCF0, "end": 0x1CDDF, "title": "Symbols for Legacy Computing Supplement", "range_label": "1CCF0 - 1CDDF"},
            {"start": 0x1CDE0, "end": 0x1CEBF, "title": "Symbols for Legacy Computing Supplement", "range_label": "1CDE0 - 1CEBF"},
        ],
    },
}


def utf16_surrogates_to_codepoint(hex_str):
    """Convert UTF-16 surrogate pair hex string to Unicode codepoint."""
    if len(hex_str) == 8:  # Surrogate pair
        high = int(hex_str[:4], 16)
        low = int(hex_str[4:], 16)
        if 0xD800 <= high <= 0xDBFF and 0xDC00 <= low <= 0xDFFF:
            return 0x10000 + ((high - 0xD800) << 10) + (low - 0xDC00)
    elif len(hex_str) == 4:  # BMP character
        return int(hex_str, 16)
    return None


def parse_tounicode_cmap(cmap_text):
    """Parse ToUnicode CMap and return glyph_id -> unicode_codepoint mapping."""
    mapping = {}

    # The format is: <glyph_id> <glyph_id> [<UTF16_code>]
    pattern = r"<([0-9A-Fa-f]+)>\s*<[0-9A-Fa-f]+>\s*\[<([0-9A-Fa-f]+)>\]"
    matches = re.findall(pattern, cmap_text)

    for glyph_id_hex, utf16_hex in matches:
        glyph_id = int(glyph_id_hex, 16)
        codepoint = utf16_surrogates_to_codepoint(utf16_hex)
        if codepoint:
            mapping[glyph_id] = codepoint

    return mapping


def find_font_and_cmap(pdf_path, font_name_pattern):
    """Find the target font and its ToUnicode CMap in the PDF."""
    doc = fitz.open(pdf_path)

    font_xref = None
    tounicode_xref = None

    # Search for the font
    for xref in range(1, doc.xref_length()):
        try:
            obj_str = doc.xref_object(xref)
            if "Font" in obj_str and font_name_pattern in obj_str:
                # Found a font object with our pattern
                base_font = doc.xref_get_key(xref, "BaseFont")
                to_unicode = doc.xref_get_key(xref, "ToUnicode")

                if font_name_pattern in str(base_font):
                    font_xref = xref
                    # Extract ToUnicode xref
                    if to_unicode and "xref" in str(to_unicode):
                        match = re.search(r"(\d+)", str(to_unicode))
                        if match:
                            tounicode_xref = int(match.group(1))
                    break
        except:
            pass

    if not font_xref or not tounicode_xref:
        doc.close()
        return None, None, None

    # Extract font data
    font_data = doc.extract_font(font_xref)
    _, _, _, font_content = font_data

    # Extract ToUnicode CMap
    cmap_stream = doc.xref_stream(tounicode_xref)
    cmap_text = cmap_stream.decode("utf-8", errors="replace")

    doc.close()
    return font_content, cmap_text, font_xref


def get_glyph_svg_path(glyph_set, glyph_name):
    """Get SVG path string for a glyph."""
    pen = SVGPathPen(glyph_set)
    try:
        glyph_set[glyph_name].draw(pen)
        return pen.getCommands()
    except Exception:
        return None


def generate_section_html(section, section_id):
    """Generate HTML for a single section/table."""
    range_start = section["start"]
    range_end = section["end"]
    title = section["title"]
    range_label = section["range_label"]

    # Calculate grid dimensions
    start_col = range_start >> 4
    end_col = range_end >> 4
    num_cols = end_col - start_col + 1

    # Generate column headers
    col_headers = []
    for col in range(start_col, end_col + 1):
        col_headers.append(f"{col:X}")

    html = f'''
    <div class="section">
        <h2>{range_label}    {title}    {range_label}</h2>
        <div class="header-row" style="grid-template-columns: 30px repeat({num_cols}, 50px);">
            <div class="header-cell"></div>
'''
    for header in col_headers:
        html += f'            <div class="header-cell">{header}</div>\n'

    html += f'''        </div>
        <div class="grid" id="grid{section_id}" style="grid-template-columns: 30px repeat({num_cols}, 50px);"></div>
    </div>
'''
    return html, start_col, end_col, range_start, range_end


def generate_test_html(output_dir, block_config):
    """Generate a test HTML file for visual comparison."""
    title = block_config["title"]
    sections = block_config["sections"]

    html_content = f'''<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background: white;
            margin: 20px;
        }}
        h1 {{
            text-align: center;
            font-size: 20px;
            margin-bottom: 30px;
        }}
        .section {{
            margin-bottom: 40px;
            page-break-after: always;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        h2 {{
            text-align: center;
            font-size: 14px;
            margin-bottom: 10px;
            font-weight: normal;
        }}
        .header-row {{
            display: grid;
            gap: 1px;
            margin-bottom: 1px;
            font-size: 9px;
        }}
        .header-cell {{
            text-align: center;
            font-weight: bold;
            padding: 2px 0;
        }}
        .grid {{
            width: fit-content;
            display: grid;
            gap: 1px;
            border: 1px solid #000;
        }}
        .row-header {{
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 10px;
            font-weight: bold;
            background: #f8f8f8;
            border-right: 1px solid #000;
        }}
        .cell {{
            border: 1px solid #ccc;
            text-align: center;
            padding: 2px;
            min-height: 55px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: space-between;
        }}
        .cell.empty {{
            background: #f0f0f0;
        }}
        .glyph {{
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .glyph img {{
            width: 28px;
            height: 28px;
        }}
        .code {{
            font-size: 7px;
            color: #333;
            font-family: monospace;
        }}
    </style>
</head>
<body>
'''

    # Generate HTML for each section
    section_configs = []
    for i, section in enumerate(sections):
        section_html, start_col, end_col, range_start, range_end = generate_section_html(section, i)
        html_content += section_html
        section_configs.append({
            "id": i,
            "startCol": start_col,
            "endCol": end_col,
            "rangeStart": range_start,
            "rangeEnd": range_end,
        })

    # Generate JavaScript to populate all grids
    html_content += '''
    <script>
        const sections = [
'''
    for cfg in section_configs:
        html_content += f'''            {{ id: {cfg["id"]}, startCol: 0x{cfg["startCol"]:X}, endCol: 0x{cfg["endCol"]:X}, rangeStart: 0x{cfg["rangeStart"]:X}, rangeEnd: 0x{cfg["rangeEnd"]:X} }},
'''

    html_content += '''        ];

        sections.forEach(section => {
            const grid = document.getElementById('grid' + section.id);

            for (let row = 0; row < 16; row++) {
                const rowHeader = document.createElement('div');
                rowHeader.className = 'row-header';
                rowHeader.textContent = row.toString(16).toUpperCase();
                grid.appendChild(rowHeader);

                for (let col = section.startCol; col <= section.endCol; col++) {
                    const codepoint = (col << 4) | row;
                    const hex = codepoint.toString(16).toUpperCase();

                    const cell = document.createElement('div');
                    cell.className = 'cell';

                    if (codepoint < section.rangeStart || codepoint > section.rangeEnd) {
                        cell.classList.add('empty');
                        cell.innerHTML = `<div class="glyph"></div><div class="code">${hex}</div>`;
                    } else {
                        cell.innerHTML = `
                            <div class="glyph">
                                <img src="U+${hex}.svg" alt="U+${hex}" onerror="this.parentElement.innerHTML='?'">
                            </div>
                            <div class="code">${hex}</div>
                        `;
                    }

                    grid.appendChild(cell);
                }
            }
        });
    </script>
</body>
</html>
'''

    html_path = os.path.join(output_dir, "index.html")
    with open(html_path, "w") as f:
        f.write(html_content)
    print(f"   Test HTML saved to: {html_path}")


def process_block(block_name, block_config):
    """Process a single Unicode block and generate SVGs."""
    print(f"\n{'='*60}")
    print(f"Processing: {block_config['title']}")
    print(f"Range: U+{block_config['range_start']:04X} - U+{block_config['range_end']:04X}")
    print(f"{'='*60}")

    pdf_path = block_config["pdf_path"]
    output_dir = block_config["output_dir"]
    range_start = block_config["range_start"]
    range_end = block_config["range_end"]
    font_pattern = block_config["font_name_pattern"]

    # Step 1: Find font and extract CMap
    print("\n1. Extracting font and CMap from PDF...")
    font_content, cmap_text, font_xref = find_font_and_cmap(pdf_path, font_pattern)

    if not font_content:
        print(f"   ERROR: Could not find font matching '{font_pattern}'")
        return

    # Parse CMap
    glyph_to_unicode = parse_tounicode_cmap(cmap_text)
    print(f"   Found {len(glyph_to_unicode)} character mappings")

    # Filter for our range
    target_chars = {
        gid: cp
        for gid, cp in glyph_to_unicode.items()
        if range_start <= cp <= range_end
    }
    print(f"   Characters in target range: {len(target_chars)}")

    # Step 2: Load font
    print("\n2. Loading font...")

    # Save font temporarily
    os.makedirs("extracted_fonts", exist_ok=True)
    font_path = f"extracted_fonts/{block_name}_font.ttf"
    with open(font_path, "wb") as f:
        f.write(font_content)

    font = TTFont(font_path)
    glyph_set = font.getGlyphSet()
    glyph_order = font.getGlyphOrder()

    # Get font metrics
    hhea = font["hhea"]
    ascent = hhea.ascent
    descent = hhea.descent
    width = 720  # Standard width
    height = ascent - descent

    print(f"   Ascent: {ascent}, Descent: {descent}")
    print(f"   Cell size: {width}x{height}")

    # Build glyph index mapping
    glyph_index_to_name = {i: name for i, name in enumerate(glyph_order)}

    # Step 3: Generate SVGs
    print(f"\n3. Generating SVGs...")
    os.makedirs(output_dir, exist_ok=True)

    generated = 0
    skipped = 0

    for glyph_id, codepoint in sorted(target_chars.items(), key=lambda x: x[1]):
        glyph_name = glyph_index_to_name.get(glyph_id)
        if not glyph_name:
            skipped += 1
            continue

        svg_path = get_glyph_svg_path(glyph_set, glyph_name)

        if not svg_path or svg_path.strip() == "":
            glyf_table = font["glyf"]
            glyph_data = glyf_table.get(glyph_name)
            if glyph_data is None or (
                hasattr(glyph_data, "numberOfContours")
                and glyph_data.numberOfContours == 0
            ):
                skipped += 1
                continue

        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">
  <g transform="translate(0, {ascent}) scale(1, -1)">
    <path d="{svg_path}" fill="currentColor"/>
  </g>
</svg>'''

        svg_output_path = os.path.join(output_dir, f"U+{codepoint:05X}.svg")
        with open(svg_output_path, "w") as f:
            f.write(svg_content)
        generated += 1

    print(f"\n   Generated: {generated} SVGs")
    print(f"   Skipped (empty): {skipped}")
    print(f"   Output directory: {output_dir}")

    # Step 4: Generate test HTML
    print("\n4. Generating test HTML...")
    generate_test_html(output_dir, block_config)

    font.close()


def main():
    print("=" * 60)
    print("Legacy Computing Symbol SVG Generator")
    print("=" * 60)

    for block_name, block_config in BLOCKS.items():
        process_block(block_name, block_config)

    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
