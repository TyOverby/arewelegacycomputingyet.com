#!/usr/bin/env python3
"""
Template generator for arewelegacycomputingyet.com

Generates the index.html page with compatibility tables from CSV data.
"""

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SectionDef:
    """A section definition with name and codepoint ranges."""

    name: str
    codepoints: set[int]
    important: bool


@dataclass
class CompatibilityRow:
    section: str
    num_chars: int
    terminal_support: dict[str, int | None]
    important: bool


@dataclass
class BlockStats:
    """Statistics for a Unicode block."""

    total_codepoints: int
    important_codepoints: int
    supported_important: int
    supported_all: int


def parse_ranges(ranges_str: str) -> set[int]:
    """Parse a space-separated list of Unicode ranges into a set of codepoints.

    Examples:
        "1FB3C-1FB67" -> {0x1FB3C, 0x1FB3D, ..., 0x1FB67}
        "1FB3C-1FB67 1FB9A-1FB9B" -> union of both ranges
    """
    codepoints = set()
    for part in ranges_str.strip().split():
        if "-" in part:
            start_str, end_str = part.split("-", 1)
            start = int(start_str, 16)
            end = int(end_str, 16)
            codepoints.update(range(start, end + 1))
        else:
            codepoints.add(int(part, 16))
    return codepoints


def load_section_csv(path: Path) -> list[SectionDef]:
    """Load a section CSV with 'section' and 'ranges' columns."""
    sections = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            section_name = row["section"].strip()
            ranges_str = row["ranges"].strip()

            important = section_name.startswith("*")
            if important:
                section_name = section_name[1:]

            codepoints = parse_ranges(ranges_str)
            sections.append(
                SectionDef(
                    name=section_name,
                    codepoints=codepoints,
                    important=important,
                )
            )
    return sections


def compute_section_compatibility(
    sections: list[SectionDef],
    emulator_data: dict[str, dict[str, str]],
) -> tuple[list[str], list[CompatibilityRow]]:
    """Compute section-based compatibility from character-level data.

    Args:
        sections: List of section definitions with codepoint sets
        emulator_data: Dict mapping emulator name -> {codepoint -> support status}

    Returns:
        Tuple of (terminal names, compatibility rows)
    """
    terminals = list(emulator_data.keys())
    rows = []

    for section in sections:
        support = {}
        for terminal in terminals:
            char_support = emulator_data[terminal]
            supported_count = 0
            for cp in section.codepoints:
                hex_code = f"U+{cp:05X}" if cp >= 0x10000 else f"U+{cp:04X}"
                status = char_support.get(hex_code, "no")
                if status == "yes":
                    supported_count += 1
                elif status == "maybe":
                    supported_count += 0.5  # Count maybe as half
            support[terminal] = int(supported_count)

        rows.append(
            CompatibilityRow(
                section=section.name,
                num_chars=len(section.codepoints),
                terminal_support=support,
                important=section.important,
            )
        )

    return terminals, rows


def calculate_totals(
    rows: list[CompatibilityRow], terminals: list[str]
) -> dict[str, tuple[int, int]]:
    """Calculate total supported / total chars for each terminal."""
    totals = {}
    total_chars = sum(r.num_chars for r in rows)

    for terminal in terminals:
        supported = sum(r.terminal_support[terminal] or 0 for r in rows)
        totals[terminal] = (supported, total_chars)

    return totals


def compute_block_stats(
    sections: list[SectionDef],
    emulator_data: dict[str, dict[str, str]],
) -> dict[str, BlockStats]:
    """Compute block statistics for each emulator.

    Returns dict mapping emulator name -> BlockStats
    """
    # Compute important and all codepoints from sections
    all_codepoints: set[int] = set()
    important_codepoints: set[int] = set()
    for section in sections:
        all_codepoints.update(section.codepoints)
        if section.important:
            important_codepoints.update(section.codepoints)

    stats = {}
    for emulator, char_support in emulator_data.items():
        supported_important = 0
        supported_all = 0

        for cp in all_codepoints:
            hex_code = f"U+{cp:05X}" if cp >= 0x10000 else f"U+{cp:04X}"
            status = char_support.get(hex_code, "no")

            if status == "yes":
                supported_all += 1
                if cp in important_codepoints:
                    supported_important += 1
            elif status == "maybe":
                supported_all += 0.5
                if cp in important_codepoints:
                    supported_important += 0.5

        stats[emulator] = BlockStats(
            total_codepoints=len(all_codepoints),
            important_codepoints=len(important_codepoints),
            supported_important=int(supported_important),
            supported_all=int(supported_all),
        )

    return stats


def render_overview(
    emulators: list[str],
    main_stats: dict[str, BlockStats] | None,
    supplement_stats: dict[str, BlockStats] | None,
) -> str:
    """Render the overview visualization with progress bars."""
    if not emulators:
        return ""

    rows_html = []
    for emulator in emulators:
        cells = [f'<td class="emulator-name">{emulator}</td>']

        # Main block progress bar
        if main_stats and emulator in main_stats:
            stats = main_stats[emulator]
            cells.append(_render_progress_cell(stats))
        else:
            cells.append(
                '<td class="progress-cell"><div class="progress-bar empty"></div></td>'
            )

        # Supplement block progress bar
        if supplement_stats and emulator in supplement_stats:
            stats = supplement_stats[emulator]
            cells.append(_render_progress_cell(stats))
        else:
            cells.append(
                '<td class="progress-cell"><div class="progress-bar empty"></div></td>'
            )

        rows_html.append(f"<tr>{''.join(cells)}</tr>")

    return f"""
    <div class="overview-section">
        <h2>Overview</h2>
        <div class="table-scroll">
            <table class="overview-table">
                <thead>
                    <tr>
                        <th>Emulator</th>
                        <th>Legacy Computing<br><span class="unicode-range">U+1FB00-U+1FBFF</span></th>
                        <th>Legacy Computing Supplement<br><span class="unicode-range">U+1CC00-U+1CEBF</span></th>
                    </tr>
                </thead>
                <tbody>
                    {"".join(rows_html)}
                </tbody>
            </table>
        </div>
    </div>
    """


def _render_progress_cell(stats: BlockStats) -> str:
    """Render a single progress bar cell."""
    total = stats.total_codepoints
    important = stats.important_codepoints
    non_important = total - important

    # Calculate widths as percentages
    important_width = (important / total * 100) if total > 0 else 0
    non_important_width = 100 - important_width

    # Calculate fill percentages within each segment
    important_fill = (
        (stats.supported_important / important * 100) if important > 0 else 0
    )
    non_important_supported = stats.supported_all - stats.supported_important
    non_important_fill = (
        (non_important_supported / non_important * 100) if non_important > 0 else 0
    )

    # Overall percentage for label
    overall_pct = (stats.supported_all / total * 100) if total > 0 else 0
    important_pct = (
        (stats.supported_important / important * 100) if important > 0 else 0
    )

    return f"""<td class="progress-cell">
        <div class="progress-bar">
            <div class="progress-segment important" style="width: {important_width:.1f}%">
                <div class="progress-fill" style="width: {important_fill:.1f}%"></div>
            </div>
            <div class="progress-marker"></div>
            <div class="progress-segment non-important" style="width: {non_important_width:.1f}%">
                <div class="progress-fill" style="width: {non_important_fill:.1f}%"></div>
            </div>
        </div>
        <div class="progress-labels">
            <span class="label-important">{important_pct:.0f}%</span>
            <span class="label-all">{overall_pct:.0f}%</span>
        </div>
    </td>"""


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
                {"".join(data_rows)}
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
    <div class="table-section show-important" data-section="{section_id}">
        <div class="section-header">
            <h2>{title}</h2>
            <div class="filter-toggle">
                <button class="filter-btn active" data-filter="important">Important</button>
                <button class="filter-btn" data-filter="all">All</button>
            </div>
        </div>
        <div class="table-scroll">
            {all_table}
            {important_table}
        </div>
    </div>
    """


def load_emulator_compatibility(csv_path: Path) -> dict[str, str]:
    """Load per-codepoint compatibility from a CSV file.

    Returns dict mapping codepoint (e.g. 'U+1FB00') to support status ('yes', 'no', 'maybe').
    """
    support = {}
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            codepoint = row["codepoint"].strip()
            supported = row["supported"].strip().lower()
            support[codepoint] = supported
    return support


def load_svg(svg_path: Path) -> str | None:
    """Load and return SVG content, or None if file doesn't exist."""
    if svg_path.exists():
        content = svg_path.read_text()
        # Remove XML declaration if present
        if content.startswith("<?xml"):
            content = content[content.index("?>") + 2 :].strip()
        return content
    return None


def render_character_grid(
    emulator_name: str,
    support_data: dict[str, str],
    svg_dir: Path,
    start_codepoint: int,
    important_codepoints: set[int],
    num_rows: int = 16,
) -> str:
    """Render a 16-column character grid for a single emulator."""
    rows_html = []

    for row in range(num_rows):
        # Calculate the row header (e.g., 1FB0, 1CC0, 1CD0, etc.)
        row_start = start_codepoint + (row * 16)
        row_prefix = f"{row_start >> 4:X}"

        row_cells = [f'<div class="grid-row-header">{row_prefix}</div>']
        row_should_show = False  # Show if any cell is important OR implemented

        for col in range(16):
            codepoint = start_codepoint + (row * 16) + col
            hex_code = (
                f"U+{codepoint:05X}" if codepoint >= 0x10000 else f"U+{codepoint:04X}"
            )

            # Get support status
            status = support_data.get(hex_code, "unknown")
            status_class = {
                "yes": "supported",
                "no": "unsupported",
                "maybe": "partial",
            }.get(status, "unknown")

            # Check if important
            is_important = codepoint in important_codepoints
            importance_class = "important" if is_important else "unimportant"

            # Row should show if any cell is important OR implemented
            is_implemented = status in ("yes", "maybe")
            if is_important or is_implemented:
                row_should_show = True

            # Load SVG
            svg_filename = f"{hex_code}.svg"
            svg_path = svg_dir / svg_filename
            svg_content = load_svg(svg_path)

            if svg_content:
                cell_content = f'<div class="glyph">{svg_content}</div>'
            else:
                cell_content = '<div class="glyph empty"></div>'

            row_cells.append(
                f'<div class="grid-cell {status_class} {importance_class}" title="{hex_code}">'
                f"{cell_content}"
                f'<div class="code">{codepoint:04X}</div>'
                f"</div>"
            )

        row_class = "grid-row" if row_should_show else "grid-row row-unimportant"
        rows_html.append(f'<div class="{row_class}">{"".join(row_cells)}</div>')

    return f'<div class="char-grid grid-{emulator_name}">{"".join(rows_html)}</div>'


def render_character_grid_section(
    title: str,
    emulators: dict[str, dict[str, str]],
    svg_dir: Path,
    start_codepoint: int,
    sections: list[SectionDef],
    num_rows: int = 16,
) -> str:
    """Render the character grid section with emulator toggle."""
    emulator_names = list(emulators.keys())

    # Compute important codepoints from sections
    important_codepoints: set[int] = set()
    for section in sections:
        if section.important:
            important_codepoints.update(section.codepoints)

    # Render emulator toggle buttons
    toggle_buttons = []
    for i, name in enumerate(emulator_names):
        active = " active" if i == 0 else ""
        toggle_buttons.append(
            f'<button class="emulator-btn{active}" data-emulator="{name}">{name}</button>'
        )

    # Render column headers
    col_headers = ['<div class="grid-col-header"></div>']  # Empty corner
    for col in range(16):
        col_headers.append(f'<div class="grid-col-header">{col:X}</div>')

    # Render grids for each emulator
    grids = []
    for i, (name, support_data) in enumerate(emulators.items()):
        display = "" if i == 0 else ' style="display: none;"'
        grid = render_character_grid(
            name, support_data, svg_dir, start_codepoint, important_codepoints, num_rows
        )
        grids.append(
            f'<div class="grid-wrapper" data-emulator="{name}"{display}>{grid}</div>'
        )

    return f"""
    <div class="char-grid-section show-important">
        <div class="section-header">
            <h2>{title}</h2>
            <div class="toggle-group">
                <div class="filter-toggle">
                    <button class="filter-btn active" data-filter="important">Important</button>
                    <button class="filter-btn" data-filter="all">All</button>
                </div>
                <div class="emulator-toggle">
                    {"".join(toggle_buttons)}
                </div>
            </div>
        </div>
        <div class="grid-container">
            <div class="grid-col-headers">{"".join(col_headers)}</div>
            {"".join(grids)}
        </div>
    </div>
    """


def load_template_files(script_dir: Path) -> tuple[str, str, str]:
    """Load the template HTML, CSS, and JavaScript files."""
    template_html = (script_dir / "template.html").read_text()
    css = (script_dir / "style.css").read_text()
    js = (script_dir / "script.js").read_text()
    return template_html, css, js


def render_page(
    overview_html: str,
    tables_html: str,
    char_grids_html: str,
    template_html: str,
    css: str,
    js: str,
) -> str:
    """Render the complete HTML page by inlining CSS and JS into the template."""
    html = template_html
    html = html.replace("{{CSS}}", css)
    html = html.replace("{{JS}}", js)
    html = html.replace("{{OVERVIEW}}", overview_html)
    html = html.replace("{{TABLES}}", tables_html)
    html = html.replace("{{CHAR_GRIDS}}", char_grids_html)
    return html


def main():
    # Find project root (two levels up from this script)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent

    csv_dir = project_root / "terminal-emulators"
    output_file = project_root / "index.html"

    tables_html = ""
    char_grids_html = ""
    all_emulators: set[str] = set()
    main_stats: dict[str, BlockStats] | None = None
    supplement_stats: dict[str, BlockStats] | None = None

    # Main block (U+1FB00-U+1FBFF)
    main_compat_dir = csv_dir / "legacy_computing_compatibility"
    main_sections_csv = csv_dir / "legacy_computing_sections.csv"

    if main_compat_dir.exists() and main_sections_csv.exists():
        # Load section definitions
        sections = load_section_csv(main_sections_csv)

        # Load character-level data for all emulators
        emulator_data = {}
        for csv_file in sorted(main_compat_dir.glob("*.csv")):
            emulator_name = csv_file.stem
            emulator_data[emulator_name] = load_emulator_compatibility(csv_file)
            all_emulators.add(emulator_name)

        if emulator_data:
            # Compute block stats for overview
            main_stats = compute_block_stats(sections, emulator_data)

            # Generate section-based compatibility table
            terminals, rows = compute_section_compatibility(sections, emulator_data)
            tables_html += render_table_section(
                "main",
                "Symbols for Legacy Computing (U+1FB00-U+1FBFF)",
                terminals,
                rows,
            )

            # Generate character grid
            svg_dir = project_root / "svgs" / "legacy_computing"
            char_grids_html += render_character_grid_section(
                "Character Support Grid (U+1FB00-U+1FBFF)",
                emulator_data,
                svg_dir,
                start_codepoint=0x1FB00,
                sections=sections,
                num_rows=16,
            )

    # Supplement block (U+1CC00-U+1CEBF) - 44 rows
    supplement_compat_dir = csv_dir / "legacy_computing_supplement_compatibility"
    supplement_sections_csv = csv_dir / "legacy_computing_supplement_sections.csv"

    if supplement_compat_dir.exists() and supplement_sections_csv.exists():
        # Load section definitions
        sections = load_section_csv(supplement_sections_csv)

        # Load character-level data for all emulators
        emulator_data = {}
        for csv_file in sorted(supplement_compat_dir.glob("*.csv")):
            emulator_name = csv_file.stem
            emulator_data[emulator_name] = load_emulator_compatibility(csv_file)
            all_emulators.add(emulator_name)

        if emulator_data:
            # Compute block stats for overview
            supplement_stats = compute_block_stats(sections, emulator_data)

            # Generate section-based compatibility table
            terminals, rows = compute_section_compatibility(sections, emulator_data)
            tables_html += render_table_section(
                "supplement",
                "Legacy Computing Supplement (U+1CC00-U+1CEBF)",
                terminals,
                rows,
            )

            # Generate character grid
            svg_dir = project_root / "svgs" / "legacy_computing_supplement"
            char_grids_html += render_character_grid_section(
                "Character Support Grid (U+1CC00-U+1CEBF)",
                emulator_data,
                svg_dir,
                start_codepoint=0x1CC00,
                sections=sections,
                num_rows=44,
            )

    # Generate overview
    overview_html = render_overview(
        sorted(all_emulators),
        main_stats,
        supplement_stats,
    )

    # Load template files and generate the page
    template_html, css, js = load_template_files(script_dir)
    html = render_page(
        overview_html, tables_html, char_grids_html, template_html, css, js
    )
    output_file.write_text(html)
    print(f"Generated {output_file}")


if __name__ == "__main__":
    main()
