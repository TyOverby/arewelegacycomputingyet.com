#!/usr/bin/env python3
"""
Template generator for arewelegacycomputingyet.com

Generates the index.html page with compatibility tables from CSV data.
"""

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CompatibilityRow:
    section: str
    num_chars: int
    terminal_support: dict[str, int | None]
    important: bool


def load_compatibility_csv(path: Path) -> tuple[list[str], list[CompatibilityRow]]:
    """Load a compatibility CSV file and return headers and rows."""
    rows = []
    terminals = []

    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        terminals = [f for f in fieldnames if f not in ("section", "num_chars")]

        for row in reader:
            support = {}
            for terminal in terminals:
                val = row.get(terminal, "").strip()
                support[terminal] = int(val) if val else None

            section_name = row["section"]
            important = section_name.startswith("*")
            if important:
                section_name = section_name[1:]  # Remove the * prefix

            rows.append(CompatibilityRow(
                section=section_name,
                num_chars=int(row["num_chars"]),
                terminal_support=support,
                important=important,
            ))

    return terminals, rows


def calculate_totals(rows: list[CompatibilityRow], terminals: list[str]) -> dict[str, tuple[int, int]]:
    """Calculate total supported / total chars for each terminal."""
    totals = {}
    total_chars = sum(r.num_chars for r in rows)

    for terminal in terminals:
        supported = sum(
            r.terminal_support[terminal] or 0
            for r in rows
        )
        totals[terminal] = (supported, total_chars)

    return totals


def render_compatibility_table(
    table_id: str,
    terminals: list[str],
    rows: list[CompatibilityRow],
    css_class: str = "",
) -> str:
    """Render a compatibility table as HTML."""
    totals = calculate_totals(rows, terminals)

    # Header row
    header_cells = "".join(f"<th>{t}</th>" for t in terminals)

    # Data rows
    data_rows = []
    for row in rows:
        cells = [f"<td>{row.section}</td>"]
        for terminal in terminals:
            val = row.terminal_support[terminal]
            if val is None:
                cells.append('<td class="unknown">?</td>')
            elif val == row.num_chars:
                cells.append('<td class="full">100%</td>')
            elif val == 0:
                cells.append('<td class="none">0%</td>')
            else:
                pct = val / row.num_chars * 100
                cells.append(f'<td class="partial">{pct:.0f}%</td>')
        data_rows.append(f"<tr>{''.join(cells)}</tr>")

    # Totals row
    total_cells = ["<td><strong>Total</strong></td>"]
    for terminal in terminals:
        supported, total = totals[terminal]
        pct = (supported / total * 100) if total > 0 else 0
        total_cells.append(f'<td class="total"><strong>{pct:.0f}%</strong></td>')
    totals_row = f"<tr class='totals-row'>{''.join(total_cells)}</tr>"

    class_attr = f' class="{css_class}"' if css_class else ""

    return f"""
        <table id="{table_id}"{class_attr}>
            <thead>
                <tr>
                    <th>Section</th>
                    {header_cells}
                </tr>
            </thead>
            <tbody>
                {''.join(data_rows)}
                {totals_row}
            </tbody>
        </table>
    """


def render_table_section(
    section_id: str,
    title: str,
    terminals: list[str],
    all_rows: list[CompatibilityRow],
) -> str:
    """Render a table section with both 'all' and 'important' variants."""
    important_rows = [r for r in all_rows if r.important]

    all_table = render_compatibility_table(
        f"{section_id}-all",
        terminals,
        all_rows,
        css_class="table-all",
    )
    important_table = render_compatibility_table(
        f"{section_id}-important",
        terminals,
        important_rows,
        css_class="table-important",
    )

    return f"""
    <div class="table-section">
        <h2>{title}</h2>
        {all_table}
        {important_table}
    </div>
    """


def render_page(tables_html: str) -> str:
    """Render the complete HTML page."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Are We Legacy Computing Yet?</title>
    <style>
        :root {{
            --bg: #1a1a2e;
            --fg: #eaeaea;
            --accent: #00d4aa;
            --muted: #888;
            --table-bg: #252540;
            --border: #3a3a5a;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: ui-monospace, 'Cascadia Code', 'Fira Code', Menlo, monospace;
            background: var(--bg);
            color: var(--fg);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 2rem;
        }}
        h1 {{
            font-size: clamp(1.5rem, 5vw, 3rem);
            margin-bottom: 1rem;
            text-align: center;
        }}
        .answer {{
            font-size: clamp(2rem, 8vw, 5rem);
            color: var(--accent);
            margin: 2rem 0;
        }}
        .subtitle {{
            color: var(--muted);
            max-width: 600px;
            line-height: 1.6;
            text-align: center;
            margin-bottom: 2rem;
        }}
        .blocks {{
            font-size: 2rem;
            margin: 2rem 0;
            letter-spacing: 0.5rem;
        }}
        a {{
            color: var(--accent);
        }}
        footer {{
            margin-top: 3rem;
            color: var(--muted);
            font-size: 0.9rem;
        }}

        /* Filter toggle */
        .filter-toggle {{
            display: flex;
            gap: 0;
            margin-bottom: 2rem;
            border-radius: 6px;
            overflow: hidden;
            border: 1px solid var(--border);
        }}
        .filter-toggle button {{
            background: var(--table-bg);
            color: var(--fg);
            border: none;
            padding: 0.75rem 1.5rem;
            cursor: pointer;
            font-family: inherit;
            font-size: 0.9rem;
            transition: background 0.2s, color 0.2s;
        }}
        .filter-toggle button:not(:last-child) {{
            border-right: 1px solid var(--border);
        }}
        .filter-toggle button:hover {{
            background: var(--border);
        }}
        .filter-toggle button.active {{
            background: var(--accent);
            color: var(--bg);
        }}

        /* Table visibility based on filter */
        body.show-all .table-important {{
            display: none;
        }}
        body.show-important .table-all {{
            display: none;
        }}

        /* Table styles */
        .table-section {{
            margin: 2rem 0;
            width: 100%;
            max-width: 900px;
        }}
        .table-section h2 {{
            font-size: 1.2rem;
            margin-bottom: 1rem;
            color: var(--accent);
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: var(--table-bg);
            border-radius: 8px;
            overflow: hidden;
        }}
        th, td {{
            padding: 0.75rem 1rem;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }}
        th {{
            background: rgba(0, 212, 170, 0.1);
            font-weight: 600;
        }}
        td.full {{
            color: #4ade80;
        }}
        td.partial {{
            color: #fbbf24;
        }}
        td.none {{
            color: #f87171;
        }}
        td.unknown {{
            color: var(--muted);
        }}
        .totals-row {{
            background: rgba(0, 212, 170, 0.05);
        }}
        .totals-row td {{
            border-bottom: none;
        }}
    </style>
</head>
<body class="show-important">
    <h1>Are We Legacy Computing Yet?</h1>
    <div class="blocks">\U0001FB00 \U0001FB01 \U0001FB02 \U0001FB03 \U0001FB04 \U0001FB05 \U0001FB06 \U0001FB07</div>
    <div class="answer">Not yet.</div>
    <p class="subtitle">
        Tracking support for Unicode's "Symbols for Legacy Computing" (U+1FB00-U+1FBFF)
        and its supplement block (U+1CC00-U+1CEBF) in modern terminal emulators and fonts.
    </p>

    <div class="filter-toggle">
        <button id="btn-important" class="active" onclick="setFilter('important')">Important</button>
        <button id="btn-all" onclick="setFilter('all')">All</button>
    </div>

    {tables_html}

    <footer>
        <a href="https://github.com/tyoverby/arewelegacycomputingyet.com">View on GitHub</a>
    </footer>

    <script>
        function setFilter(filter) {{
            document.body.className = 'show-' + filter;
            document.getElementById('btn-important').classList.toggle('active', filter === 'important');
            document.getElementById('btn-all').classList.toggle('active', filter === 'all');
        }}
    </script>
</body>
</html>
"""


def main():
    # Find project root (two levels up from this script)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent

    csv_dir = project_root / "terminal-emulators"
    output_file = project_root / "index.html"

    tables_html = ""

    # Load and render main block compatibility
    main_csv = csv_dir / "legacy_computing_compatibility.csv"
    if main_csv.exists():
        terminals, rows = load_compatibility_csv(main_csv)
        tables_html += render_table_section(
            "main",
            "Symbols for Legacy Computing (U+1FB00-U+1FBFF)",
            terminals,
            rows,
        )

    # Load and render supplement block compatibility
    supplement_csv = csv_dir / "legacy_computing_supplement_compatibility.csv"
    if supplement_csv.exists():
        terminals, rows = load_compatibility_csv(supplement_csv)
        tables_html += render_table_section(
            "supplement",
            "Legacy Computing Supplement (U+1CC00-U+1CEBF)",
            terminals,
            rows,
        )

    # Generate the page
    html = render_page(tables_html)
    output_file.write_text(html)
    print(f"Generated {output_file}")


if __name__ == "__main__":
    main()
