#!/usr/bin/env python3
"""
Gridded SVG generator for arewelegacycomputingyet.com

Takes a text file containing legacy computing Unicode characters and produces
an HTML file showing each character rendered as its SVG path in a grid layout.

Usage:
    python scripts/gridded_svg_gen.py <input.txt> [output.html]

If output path is omitted, writes <input>.html alongside the input file.
"""

import html
import re
import sys
from pathlib import Path


def find_svg(codepoint: int, svg_dirs: list[Path]) -> str | None:
    """Return inline SVG content for the given codepoint, or None."""
    hex_code = f"U+{codepoint:05X}" if codepoint >= 0x10000 else f"U+{codepoint:04X}"
    for svg_dir in svg_dirs:
        svg_path = svg_dir / f"{hex_code}.svg"
        if svg_path.exists():
            content = svg_path.read_text(encoding="utf-8")
            if content.startswith("<?xml"):
                content = content[content.index("?>") + 2 :].strip()
            return content
    return None


def parse_grid(text: str) -> list[list[str]]:
    """Split text into a 2D list of characters, padding rows to uniform width."""
    lines = text.split("\n")
    # Drop a single trailing blank line (from files ending with \n)
    if lines and lines[-1] == "":
        lines = lines[:-1]

    max_len = max((len(line) for line in lines), default=0)
    return [list(line) + [" "] * (max_len - len(line)) for line in lines]


def render_cell(char: str, svg_dirs: list[Path]) -> str:
    cp = ord(char)
    svg = find_svg(cp, svg_dirs)

    cp_str = f'U+{cp:04X}' if cp < 0x10000 else f'U+{cp:05X}'
    if svg:
        return f'<div class="cell glyph" data-cp="{cp_str}">{svg}</div>'
    elif cp == 0x2588:  # █ FULL BLOCK
        return f'<div class="cell filled" data-cp="{cp_str}"></div>'
    elif cp == 0x258C:  # ▌ LEFT HALF BLOCK
        return f'<div class="cell half-left" data-cp="{cp_str}"></div>'
    elif char.strip() == "":
        return f'<div class="cell space" data-cp="{cp_str}"></div>'
    else:
        return f'<div class="cell unknown" data-cp="{cp_str}"></div>'


def render_grid(text: str, svg_dirs: list[Path]) -> str:
    """Render text content as a grid of SVG cells."""
    grid = parse_grid(text)
    if not grid:
        return ""
    rows_html = "\n".join(
        '<div class="row">'
        + "".join(render_cell(ch, svg_dirs) for ch in row)
        + "</div>"
        for row in grid
    )
    return f'<div class="grid">\n{rows_html}\n</div>'


def default_output_path(input_path: Path) -> Path:
    """Derive output path: foo.input.html → foo.html, foo.txt → foo.html."""
    name = input_path.name
    if name.endswith(".input.html"):
        return input_path.with_name(name[: -len(".input.html")] + ".html")
    return input_path.with_suffix(".html")


def generate_html(text_path: Path, svg_dirs: list[Path]) -> str:
    raw = text_path.read_text(encoding="utf-8")

    pre_match = re.search(r"<pre>(.*?)</pre>?", raw, re.DOTALL)
    if pre_match:
        pre_text = html.unescape(pre_match.group(1)).strip()
        grid_html = render_grid(pre_text, svg_dirs)
        body_content = raw[: pre_match.start()] + grid_html + raw[pre_match.end() :]
    else:
        body_content = render_grid(raw, svg_dirs)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{text_path.stem.removesuffix(".input")}</title>
<style>
  :root {{
    --bg:  #1d2021;
    --fg:  #d4be98;
    --cell: 32px;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: var(--bg);
    color: var(--fg);
    padding: 2rem;
    font-family: monospace;
    line-height: 1.5;
  }}
  a {{ color: #7daea3; }}
  p {{ margin-bottom: 1rem; }}
  .grid {{
    display: block;
    line-height: 0;
    margin: 1rem 0;
  }}
  .row {{
    display: flex;
  }}
  .cell {{
    position: relative;
    width: var(--cell);
    height: var(--cell);
    flex-shrink: 0;
    box-shadow: inset 0 0 0 1px #3c3836;
  }}
  .cell:hover::after, .cell.active::after {{
    content: '';
    position: absolute;
    inset: 0;
    border: 1px solid #7daea3;
    pointer-events: none;
    z-index: 1;
  }}
  .cell.glyph svg {{
    width: var(--cell);
    height: var(--cell);
    display: block;
    fill: var(--fg);
  }}
  .cell.filled {{
    background: var(--fg);
  }}
  .cell.half-left {{
    background: linear-gradient(to right, var(--fg) 50%, transparent 50%);
  }}
  .cell.unknown {{
    background: #3a2a1a;
  }}
  #popover {{
    position: fixed;
    background: #282828;
    color: #d4be98;
    border: 1px solid #7daea3;
    padding: 2px 6px;
    font-family: monospace;
    font-size: 0.75rem;
    pointer-events: none;
    display: none;
    z-index: 100;
  }}
</style>
</head>
<body>
{body_content}
<div id="popover"></div>
<script>
  const popover = document.getElementById('popover');
  let pinned = null;

  function showAt(cell, x, y) {{
    popover.textContent = cell.dataset.cp;
    popover.style.display = 'block';
    place(x, y);
  }}

  function place(x, y) {{
    const pad = 8;
    popover.style.left = '0';
    popover.style.top = '0';
    const pw = popover.offsetWidth, ph = popover.offsetHeight;
    let left = x + pad;
    let top = y - ph - pad;
    if (left + pw > window.innerWidth) left = x - pw - pad;
    if (top < 0) top = y + pad;
    popover.style.left = left + 'px';
    popover.style.top = top + 'px';
  }}

  function hide() {{
    popover.style.display = 'none';
    if (pinned) {{ pinned.classList.remove('active'); pinned = null; }}
  }}

  document.querySelectorAll('.cell[data-cp]').forEach(cell => {{
    cell.addEventListener('mouseenter', e => {{
      if (!pinned) showAt(cell, e.clientX, e.clientY);
    }});
    cell.addEventListener('mousemove', e => {{
      if (!pinned) place(e.clientX, e.clientY);
    }});
    cell.addEventListener('mouseleave', () => {{
      if (!pinned) hide();
    }});
    cell.addEventListener('click', e => {{
      e.stopPropagation();
      if (pinned === cell) {{
        hide();
      }} else {{
        if (pinned) pinned.classList.remove('active');
        pinned = cell;
        pinned.classList.add('active');
        showAt(cell, e.clientX, e.clientY);
      }}
    }});
  }});

  document.addEventListener('click', hide);
</script>
</body>
</html>"""


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <input.txt> [output.html]", file=sys.stderr)
        sys.exit(1)

    text_path = Path(sys.argv[1])
    if not text_path.exists():
        print(f"Error: {text_path} not found", file=sys.stderr)
        sys.exit(1)

    output_path = (
        Path(sys.argv[2]) if len(sys.argv) >= 3 else default_output_path(text_path)
    )

    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    svg_dirs = [
        project_root / "svgs" / "legacy_computing",
        project_root / "svgs" / "legacy_computing_supplement",
    ]

    html = generate_html(text_path, svg_dirs)
    output_path.write_text(html, encoding="utf-8")
    print(f"Generated {output_path}")


if __name__ == "__main__":
    main()
