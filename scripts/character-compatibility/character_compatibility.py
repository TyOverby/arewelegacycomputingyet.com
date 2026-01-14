#!/usr/bin/env python3
"""Interactive character-by-character compatibility checker for terminal emulators."""

import argparse
import csv
import sys

import readchar

# Unicode block definitions
BLOCKS = {
    "legacy_computing": {
        "range_start": 0x1FB00,
        "range_end": 0x1FBFF,
        "title": "Symbols for Legacy Computing",
    },
    "legacy_computing_supplement": {
        "range_start": 0x1CC00,
        "range_end": 0x1CEBF,
        "title": "Symbols for Legacy Computing Supplement",
    },
}


def get_range_input(prompt: str, block_start: int, block_end: int) -> tuple[int, int] | None:
    """Prompt user for a hex range and return (start, end) codepoints."""
    print(f"\n{prompt}")
    try:
        range_str = input("Enter range (e.g., 1FB00-1FB0F): ").strip().upper()
        if "-" in range_str:
            start_str, end_str = range_str.split("-", 1)
        else:
            # Single codepoint
            start_str = end_str = range_str

        # Remove U+ prefix if present
        start_str = start_str.replace("U+", "")
        end_str = end_str.replace("U+", "")

        start = int(start_str, 16)
        end = int(end_str, 16)

        # Validate range is within block
        if start < block_start or end > block_end or start > end:
            print(f"Range must be within U+{block_start:04X}-U+{block_end:04X}")
            return None

        return (start, end)
    except (ValueError, KeyboardInterrupt):
        print("Invalid range format.")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Interactive character compatibility checker for terminal emulators"
    )
    parser.add_argument("terminal_name", help="Name of the terminal emulator")
    parser.add_argument(
        "block",
        choices=["legacy_computing", "legacy_computing_supplement"],
        help="Unicode block to test",
    )
    args = parser.parse_args()

    block = BLOCKS[args.block]
    start = block["range_start"]
    end = block["range_end"]
    title = block["title"]

    output_file = f"{args.terminal_name}.csv"
    results: dict[int, str] = {}  # codepoint -> "yes"/"no"

    print(f"\nTesting {title} (U+{start:04X} - U+{end:04X})")
    print(f"Terminal: {args.terminal_name}")
    print(f"Output: {output_file}")
    print("\nKeys:")
    print("  y = supported")
    print("  n = not supported")
    print("  m = maybe")
    print("  Y = confirm a range as supported")
    print("  N = confirm a range as not supported")
    print("  M = confirm a range as maybe")
    print("  s = skip")
    print("  S = skip to a specific codepoint")
    print("  q = quit (saves progress)")
    print("-" * 40)

    codepoint = start
    while codepoint <= end:
        char = chr(codepoint)
        hex_code = f"U+{codepoint:04X}"

        # Show status
        status = results.get(codepoint, "?")
        status_display = {"yes": "[Y]", "no": "[N]", "maybe": "[M]", "?": "[ ]"}.get(status, "[ ]")
        print(f"\r{hex_code}: {char}  {status_display}  ", end="", flush=True)

        key = readchar.readkey()

        if key == "y":
            results[codepoint] = "yes"
            codepoint += 1
        elif key == "n":
            results[codepoint] = "no"
            codepoint += 1
        elif key == "m":
            results[codepoint] = "maybe"
            codepoint += 1
        elif key == "Y":
            range_result = get_range_input("Mark range as SUPPORTED:", start, end)
            if range_result:
                r_start, r_end = range_result
                for cp in range(r_start, r_end + 1):
                    results[cp] = "yes"
                print(f"Marked U+{r_start:04X}-U+{r_end:04X} as supported")
                codepoint = min(r_end + 1, end)
        elif key == "N":
            range_result = get_range_input("Mark range as NOT SUPPORTED:", start, end)
            if range_result:
                r_start, r_end = range_result
                for cp in range(r_start, r_end + 1):
                    results[cp] = "no"
                print(f"Marked U+{r_start:04X}-U+{r_end:04X} as not supported")
                codepoint = min(r_end + 1, end)
        elif key == "M":
            range_result = get_range_input("Mark range as MAYBE:", start, end)
            if range_result:
                r_start, r_end = range_result
                for cp in range(r_start, r_end + 1):
                    results[cp] = "maybe"
                print(f"Marked U+{r_start:04X}-U+{r_end:04X} as maybe")
                codepoint = min(r_end + 1, end)
        elif key == "s":
            codepoint += 1
        elif key == "S":
            print("\nSkip to codepoint:")
            try:
                cp_str = input("Enter codepoint (e.g., 1FB50): ").strip().upper().replace("U+", "")
                target = int(cp_str, 16)
                if start <= target <= end:
                    codepoint = target
                else:
                    print(f"Codepoint must be within U+{start:04X}-U+{end:04X}")
            except (ValueError, KeyboardInterrupt):
                print("Invalid codepoint.")
        elif key == "q":
            print("\n\nQuitting early...")
            break
        elif key == readchar.key.LEFT or key == "h":
            if codepoint > start:
                codepoint -= 1
        elif key == readchar.key.RIGHT or key == "l":
            if codepoint < end:
                codepoint += 1

    # Write results to CSV
    if results:
        with open(output_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["codepoint", "supported"])
            writer.writeheader()
            for cp in sorted(results.keys()):
                writer.writerow({"codepoint": f"U+{cp:04X}", "supported": results[cp]})
        print(f"\nSaved {len(results)} results to {output_file}")
    else:
        print("\nNo results to save.")


if __name__ == "__main__":
    main()
