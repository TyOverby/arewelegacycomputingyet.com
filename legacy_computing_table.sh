#!/bin/bash
# Displays the Unicode "Symbols for Legacy Computing" block (U+1FB00-U+1FBFF)
# in a colorful grid with box-drawing characters

# Check if stdout is a TTY
if [ -t 1 ]; then
    # ANSI color codes
    RESET="\033[0m"
    BOLD="\033[1m"
    DIM="\033[2m"

    # Colors
    CYAN="\033[36m"
    YELLOW="\033[33m"
    GREEN="\033[32m"
    MAGENTA="\033[35m"
    BLUE="\033[34m"
    WHITE="\033[97m"
    GRAY="\033[90m"
    BG_BLACK="\033[40m"
else
    # No colors when piped
    RESET=""
    BOLD=""
    DIM=""
    CYAN=""
    YELLOW=""
    GREEN=""
    MAGENTA=""
    BLUE=""
    WHITE=""
    GRAY=""
    BG_BLACK=""
fi

# Box drawing characters - double outer border, single inner lines
TL="╔"  # top-left (double)
TR="╗"  # top-right (double)
BL="╚"  # bottom-left (double)
BR="╝"  # bottom-right (double)
H="═"   # horizontal double
V="║"   # vertical double
HL="─"  # horizontal single (inner)
VL="│"  # vertical single (inner)
# Mixed junctions (double outer connects to single inner)
TJ="╤"  # top junction (double horiz, single down)
BJ="╧"  # bottom junction (double horiz, single up)
LJ="╟"  # left junction (double vert, single right)
RJ="╢"  # right junction (double vert, single left)
CJ="┼"  # center junction (single both)

# Function to print a Unicode character from a code point
print_char() {
    local code=$1
    printf "\\U$(printf '%08X' $code)"
}

# Function to check if a code point is assigned
is_assigned() {
    local code=$1
    # Unassigned range: U+1FBFB-U+1FBFF (print up through U+1FBFA)
    if (( code >= 0x1FBFB && code <= 0x1FBFF )); then
        return 1
    fi
    return 0
}

# Column header width
COL_WIDTH=4

# Print column headers
echo -n "      "
for col in 0 1 2 3 4 5 6 7 8 9 A B C D E F; do
    printf " %s  " "$col"
done
echo ""

# Print top border
echo -n "     ${TL}"
for col in {0..15}; do
    echo -n "${H}${H}${H}"
    if [ $col -lt 15 ]; then
        echo -n "${TJ}"
    fi
done
echo "${TR}"

# Print each row (16 rows: 1FB0x through 1FBFx)
for row in {0..15}; do
    # Row header (base code point)
    row_hex=$(printf '%X' $row)
    echo -n "1FB${row_hex} ${V}"

    for col in {0..15}; do
        col_hex=$(printf '%X' $col)
        code_point=$((0x1FB00 + row * 16 + col))

        if is_assigned $code_point; then
            # Print the character with black background and coloring based on category
            if (( code_point <= 0x1FB3B )); then
                # Block sextants - cyan
                color="${CYAN}"
            elif (( code_point <= 0x1FB6F )); then
                # Diagonal/triangular - magenta
                color="${MAGENTA}"
            elif (( code_point <= 0x1FB9F )); then
                # One-eighth blocks and fills - blue
                color="${BLUE}"
            elif (( code_point <= 0x1FBAF )); then
                # Box drawing diagonals - green
                color="${GREEN}"
            elif (( code_point <= 0x1FBCA )); then
                # Legacy symbols - yellow
                color="${YELLOW}"
            else
                # Segmented digits and others - white
                color="${WHITE}"
            fi

            printf " "
            echo -e -n "${BG_BLACK}${color}"
            print_char $code_point
            echo -e -n "${RESET}"
            printf " "
        else
            # Unassigned - show dimmed dot
            printf " "
            echo -e -n "${DIM}·${RESET}"
            printf " "
        fi

        # Use double line for rightmost border, single for inner
        if [ $col -eq 15 ]; then
            echo -n "${V}"
        else
            echo -n "${VL}"
        fi
    done
    echo ""

    # Print row separator (except after last row)
    if [ $row -lt 15 ]; then
        echo -n "     ${LJ}"
        for col in {0..15}; do
            echo -n "${HL}${HL}${HL}"
            if [ $col -lt 15 ]; then
                echo -n "${CJ}"
            fi
        done
        echo "${RJ}"
    fi
done

# Print bottom border
echo -n "     ${BL}"
for col in {0..15}; do
    echo -n "${H}${H}${H}"
    if [ $col -lt 15 ]; then
        echo -n "${BJ}"
    fi
done
echo "${BR}"
