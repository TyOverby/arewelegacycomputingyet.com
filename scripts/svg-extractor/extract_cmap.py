#!/usr/bin/env python3
"""Extract ToUnicode CMap from PDF to find character mappings."""

import fitz
import re

PDF_PATH = "../../sources/U1FB00_symbols_for_legacy_computing.pdf"


def extract_cmap():
    doc = fitz.open(PDF_PATH)

    # Look for the KreativeSquareUnibook font's ToUnicode CMap
    # Font xref is 41 from our earlier analysis

    print("=== Searching for ToUnicode CMaps ===\n")

    # Get all objects in the PDF
    xref_count = doc.xref_length()
    print(f"Total objects in PDF: {xref_count}")

    for xref in range(1, xref_count):
        try:
            obj_type = doc.xref_get_key(xref, "Type")
            subtype = doc.xref_get_key(xref, "Subtype")

            # Look for font objects
            if "Font" in str(obj_type) or "Font" in str(subtype):
                base_font = doc.xref_get_key(xref, "BaseFont")
                to_unicode = doc.xref_get_key(xref, "ToUnicode")

                if "Kreative" in str(base_font) or "Square" in str(base_font):
                    print(f"Font at xref {xref}:")
                    print(f"  BaseFont: {base_font}")
                    print(f"  ToUnicode: {to_unicode}")

                    # Try to get the ToUnicode stream
                    if to_unicode and "xref" in str(to_unicode):
                        # Parse the xref number from the reference
                        match = re.search(r"(\d+)", str(to_unicode))
                        if match:
                            tounicode_xref = int(match.group(1))
                            stream = doc.xref_stream(tounicode_xref)
                            if stream:
                                print(f"\n  ToUnicode stream ({len(stream)} bytes):")
                                # Decode and show the CMap
                                try:
                                    text = stream.decode("utf-8", errors="replace")
                                    print(text[:2000])
                                    if len(text) > 2000:
                                        print("... (truncated)")
                                except:
                                    print("  (binary data)")
        except:
            pass

    doc.close()


def parse_cmap_to_dict(cmap_text):
    """Parse a ToUnicode CMap and return a dict mapping CIDs to Unicode."""
    mapping = {}

    # Look for bfchar sections
    bfchar_pattern = r"beginbfchar\s+(.*?)endbfchar"
    matches = re.findall(bfchar_pattern, cmap_text, re.DOTALL)

    for match in matches:
        # Parse individual mappings like <0001> <1FB00>
        entries = re.findall(r"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", match)
        for cid_hex, unicode_hex in entries:
            cid = int(cid_hex, 16)
            unicode_val = int(unicode_hex, 16)
            mapping[cid] = unicode_val

    # Look for bfrange sections
    bfrange_pattern = r"beginbfrange\s+(.*?)endbfrange"
    matches = re.findall(bfrange_pattern, cmap_text, re.DOTALL)

    for match in matches:
        # Parse range mappings like <0001> <0010> <1FB00>
        entries = re.findall(
            r"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", match
        )
        for start_hex, end_hex, unicode_start_hex in entries:
            start_cid = int(start_hex, 16)
            end_cid = int(end_hex, 16)
            unicode_start = int(unicode_start_hex, 16)

            for i, cid in enumerate(range(start_cid, end_cid + 1)):
                mapping[cid] = unicode_start + i

    return mapping


if __name__ == "__main__":
    extract_cmap()
