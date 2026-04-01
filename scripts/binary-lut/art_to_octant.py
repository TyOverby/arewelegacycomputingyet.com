#!/usr/bin/env python3
"""Convert a text art file to octant-encoded Unicode.

Each 2×4 block of input characters maps to one octant cell.
Non-space characters are treated as filled pixels.
"""

import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))

# Load LUT from data.txt (one character per line, 0-indexed)
lut = []
with open(os.path.join(script_dir, "data.txt"), encoding="utf-8") as f:
    for line in f:
        lut.append(line.rstrip("\n"))

def convert(path):
    with open(path, encoding="utf-8") as f:
        rows = [line.rstrip("\n") for line in f]

    # Pad rows to uniform width
    width = max((len(r) for r in rows), default=0)
    rows = [r.ljust(width) for r in rows]

    out_rows = -(-len(rows) // 4)   # ceil divide
    out_cols = -(-width // 2)       # ceil divide

    for out_row in range(out_rows):
        line = []
        for out_col in range(out_cols):
            bits = 0
            for y in range(4):
                for x in range(2):
                    src_row = out_row * 4 + y
                    src_col = out_col * 2 + x
                    if src_row < len(rows) and src_col < len(rows[src_row]):
                        if rows[src_row][src_col] != " ":
                            bits |= 1 << (y * 2 + x)
            line.append(lut[bits])
        print("".join(line))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <art_file>", file=sys.stderr)
        sys.exit(1)
    convert(sys.argv[1])
