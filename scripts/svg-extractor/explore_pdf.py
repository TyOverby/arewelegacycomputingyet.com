#!/usr/bin/env python3
"""Explore the PDF structure to understand how glyphs are stored."""

import fitz  # PyMuPDF

PDF_PATH = "../../sources/U1FB00_symbols_for_legacy_computing.pdf"


def explore_pdf():
    doc = fitz.open(PDF_PATH)

    print(f"Number of pages: {len(doc)}")
    print(f"Metadata: {doc.metadata}")
    print()

    # Check embedded fonts
    print("=== Embedded Fonts ===")
    for page_num in range(len(doc)):
        page = doc[page_num]
        fonts = page.get_fonts()
        print(f"Page {page_num + 1} fonts: {fonts}")
    print()

    # Look at page 2 which has the main character chart
    page = doc[1]  # Page 2 (0-indexed)

    print("=== Page 2 Content Analysis ===")
    print(f"Page size: {page.rect}")

    # Get all drawings/paths on the page
    paths = page.get_drawings()
    print(f"Number of drawing paths: {len(paths)}")

    if paths:
        print("\nFirst 5 paths:")
        for i, path in enumerate(paths[:5]):
            print(f"  Path {i}: {path}")

    # Get text blocks with positioning
    print("\n=== Text Extraction ===")
    blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)

    # Look at the structure
    print(f"Number of blocks: {len(blocks.get('blocks', []))}")

    # Find image/xobject content
    print("\n=== Images/XObjects ===")
    images = page.get_images()
    print(f"Number of images: {len(images)}")

    # Extract the raw content stream
    print("\n=== Raw Content Preview ===")
    xref = page.xref
    content = doc.xref_stream(xref)
    if content:
        print(f"Content stream length: {len(content)} bytes")
        # Show first 500 chars
        preview = content[:500].decode('latin-1', errors='replace')
        print(f"Preview:\n{preview}")

    doc.close()


if __name__ == "__main__":
    explore_pdf()
