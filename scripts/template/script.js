// Per-section filter toggle (for both table sections and grid sections)
document.querySelectorAll(".filter-toggle").forEach((toggle) => {
    toggle.querySelectorAll("button").forEach((btn) => {
        btn.addEventListener("click", () => {
            const filter = btn.dataset.filter;
            const section = btn.closest(".table-section, .char-grid-section");

            // Update active button
            toggle
                .querySelectorAll("button")
                .forEach((b) => b.classList.remove("active"));
            btn.classList.add("active");

            // Update section class
            section.classList.remove("show-important", "show-all");
            section.classList.add("show-" + filter);
        });
    });
});

// Demo grid popover
const demoPopover = document.getElementById("demo-popover");
if (demoPopover) {
    let demoPinned = null;

    function demoShowAt(cell, x, y) {
        demoPopover.textContent = cell.dataset.cp;
        demoPopover.style.display = "block";
        demoPlace(x, y);
    }
    function demoPlace(x, y) {
        const pad = 8;
        demoPopover.style.left = "0";
        demoPopover.style.top = "0";
        const pw = demoPopover.offsetWidth,
            ph = demoPopover.offsetHeight;
        let left = x + pad,
            top = y - ph - pad;
        if (left + pw > window.innerWidth) left = x - pw - pad;
        if (top < 0) top = y + pad;
        demoPopover.style.left = left + "px";
        demoPopover.style.top = top + "px";
    }
    function demoHide() {
        demoPopover.style.display = "none";
        if (demoPinned) {
            demoPinned.classList.remove("active");
            demoPinned = null;
        }
    }
    document.querySelectorAll(".demo-cell[data-cp]").forEach((cell) => {
        cell.addEventListener("mouseenter", (e) => {
            if (!demoPinned) demoShowAt(cell, e.clientX, e.clientY);
        });
        cell.addEventListener("mousemove", (e) => {
            if (!demoPinned) demoPlace(e.clientX, e.clientY);
        });
        cell.addEventListener("mouseleave", () => {
            if (!demoPinned) demoHide();
        });
        cell.addEventListener("click", (e) => {
            e.stopPropagation();
            if (demoPinned === cell) {
                demoHide();
            } else {
                if (demoPinned) demoPinned.classList.remove("active");
                demoPinned = cell;
                demoPinned.classList.add("active");
                demoShowAt(cell, e.clientX, e.clientY);
            }
        });
    });
    document.addEventListener("click", demoHide);
}

// Emulator grid toggle
document.querySelectorAll(".emulator-toggle").forEach((toggle) => {
    toggle.querySelectorAll("button").forEach((btn) => {
        btn.addEventListener("click", () => {
            const emulator = btn.dataset.emulator;
            const section = btn.closest(".char-grid-section");

            // Update active button
            toggle
                .querySelectorAll("button")
                .forEach((b) => b.classList.remove("active"));
            btn.classList.add("active");

            // Show/hide grids
            section.querySelectorAll(".grid-wrapper").forEach((wrapper) => {
                wrapper.style.display =
                    wrapper.dataset.emulator === emulator ? "" : "none";
            });
        });
    });
});
