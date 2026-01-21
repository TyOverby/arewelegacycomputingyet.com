// Per-section filter toggle (for both table sections and grid sections)
document.querySelectorAll('.filter-toggle').forEach(toggle => {
    toggle.querySelectorAll('button').forEach(btn => {
        btn.addEventListener('click', () => {
            const filter = btn.dataset.filter;
            const section = btn.closest('.table-section, .char-grid-section');

            // Update active button
            toggle.querySelectorAll('button').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Update section class
            section.classList.remove('show-important', 'show-all');
            section.classList.add('show-' + filter);
        });
    });
});

// Emulator grid toggle
document.querySelectorAll('.emulator-toggle').forEach(toggle => {
    toggle.querySelectorAll('button').forEach(btn => {
        btn.addEventListener('click', () => {
            const emulator = btn.dataset.emulator;
            const section = btn.closest('.char-grid-section');

            // Update active button
            toggle.querySelectorAll('button').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Show/hide grids
            section.querySelectorAll('.grid-wrapper').forEach(wrapper => {
                wrapper.style.display = wrapper.dataset.emulator === emulator ? '' : 'none';
            });
        });
    });
});
