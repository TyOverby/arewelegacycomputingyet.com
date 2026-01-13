#!/bin/bash
# Displays the Unicode "Symbols for Legacy Computing Supplement" block (U+1CC00-U+1CEBF)
# in a colorful grid with box-drawing characters
# Based on Unicode Standard Version 17.0

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
    RED="\033[31m"
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
    RED=""
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
    # Unassigned: U+1CCFD-U+1CCFF
    if (( code >= 0x1CCFD && code <= 0x1CCFF )); then
        return 1
    fi
    # Unassigned: U+1CEB4-U+1CEB9
    if (( code >= 0x1CEB4 && code <= 0x1CEB9 )); then
        return 1
    fi
    # Out of range (block ends at 1CEBF)
    if (( code > 0x1CEBF )); then
        return 1
    fi
    return 0
}

# Function to get color based on character category
get_color() {
    local code=$1

    if (( code <= 0x1CC04 )); then
        # Game sprites (go-karts, stick figures)
        echo "${YELLOW}"
    elif (( code <= 0x1CC1A )); then
        # Rule segments & Schematic symbols
        echo "${GREEN}"
    elif (( code <= 0x1CC20 )); then
        # Box drawing characters
        echo "${CYAN}"
    elif (( code <= 0x1CC2F )); then
        # Separated mosaic quadrants
        echo "${BLUE}"
    elif (( code <= 0x1CC3F )); then
        # Circle segments
        echo "${MAGENTA}"
    elif (( code <= 0x1CC47 )); then
        # Fill characters
        echo "${BLUE}"
    elif (( code <= 0x1CCA5 )); then
        # Game sprites
        echo "${YELLOW}"
    elif (( code <= 0x1CCB1 )); then
        # Faces
        echo "${RED}"
    elif (( code <= 0x1CCD5 )); then
        # Icons & Chess symbols
        echo "${WHITE}"
    elif (( code <= 0x1CCF9 )); then
        # Outlined letters & digits
        echo "${CYAN}"
    elif (( code <= 0x1CCFC )); then
        # Terminal graphic characters (snake, saucer, nose)
        echo "${YELLOW}"
    elif (( code <= 0x1CDE5 )); then
        # Block octants
        echo "${BLUE}"
    elif (( code <= 0x1CDFF )); then
        # Game sprites (runners, robots, etc)
        echo "${YELLOW}"
    elif (( code <= 0x1CE19 )); then
        # Terminal graphics, box drawing
        echo "${CYAN}"
    elif (( code <= 0x1CE50 )); then
        # Large type pieces
        echo "${GREEN}"
    elif (( code <= 0x1CE8F )); then
        # Separated mosaic sextants
        echo "${BLUE}"
    elif (( code <= 0x1CEAF )); then
        # Block elements (sixteenths, quarters)
        echo "${MAGENTA}"
    elif (( code <= 0x1CEB3 )); then
        # Smalltalk symbols
        echo "${WHITE}"
    else
        # Terminal graphic characters (fruit symbols, etc)
        echo "${YELLOW}"
    fi
}

# Column header width
COL_WIDTH=4

# Print column headers
echo -n "       "
for col in 0 1 2 3 4 5 6 7 8 9 A B C D E F; do
    printf " %s  " "$col"
done
echo ""

# Print top border
echo -n "      ${TL}"
for col in {0..15}; do
    echo -n "${H}${H}${H}"
    if [ $col -lt 15 ]; then
        echo -n "${TJ}"
    fi
done
echo "${TR}"

# Print each row (44 rows: 1CC0x through 1CEBx)
for row in {0..43}; do
    # Calculate the row prefix (1CC0, 1CC1, ... 1CCF, 1CD0, ... 1CDF, 1CE0, ... 1CEB)
    if (( row < 16 )); then
        row_prefix="1CC"
        row_hex=$(printf '%X' $row)
    elif (( row < 32 )); then
        row_prefix="1CD"
        row_hex=$(printf '%X' $((row - 16)))
    else
        row_prefix="1CE"
        row_hex=$(printf '%X' $((row - 32)))
    fi

    echo -n " ${row_prefix}${row_hex} ${V}"

    for col in {0..15}; do
        col_hex=$(printf '%X' $col)
        code_point=$((0x1CC00 + row * 16 + col))

        if is_assigned $code_point; then
            color=$(get_color $code_point)
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
    if [ $row -lt 43 ]; then
        echo -n "      ${LJ}"
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
echo -n "      ${BL}"
for col in {0..15}; do
    echo -n "${H}${H}${H}"
    if [ $col -lt 15 ]; then
        echo -n "${BJ}"
    fi
done
echo "${BR}"

echo ""
echo "Legend:"
echo -e "  ${YELLOW}■${RESET} Game sprites & terminal graphics"
echo -e "  ${GREEN}■${RESET} Schematic symbols & large type pieces"
echo -e "  ${CYAN}■${RESET} Box drawing & outlined letters/digits"
echo -e "  ${BLUE}■${RESET} Block mosaics (quadrants, sextants, octants)"
echo -e "  ${MAGENTA}■${RESET} Circle segments & block elements"
echo -e "  ${WHITE}■${RESET} Chess symbols & icons"
echo -e "  ${RED}■${RESET} Faces"
echo -e "  ${DIM}·${RESET}  Unassigned"
