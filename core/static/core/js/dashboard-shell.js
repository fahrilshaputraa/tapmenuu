(() => {
    const sidebar = document.querySelector('[data-dashboard-sidebar]');
    const backdrop = document.querySelector('[data-dashboard-sidebar-backdrop]');
    const menuButtons = document.querySelectorAll('[data-dashboard-menu-button]');
    const desktopQuery = window.matchMedia('(min-width: 768px)');

    if (!sidebar || !menuButtons.length) {
        return;
    }

    const setOpen = (isOpen) => {
        const isDesktop = desktopQuery.matches;
        const shouldOpen = isOpen && !isDesktop;

        sidebar.classList.toggle('-translate-x-full', !shouldOpen);
        sidebar.classList.toggle('translate-x-0', shouldOpen);
        sidebar.setAttribute('aria-hidden', String(!shouldOpen && !isDesktop));

        if (backdrop) {
            backdrop.classList.toggle('hidden', !shouldOpen);
        }

        menuButtons.forEach((button) => {
            button.setAttribute('aria-expanded', String(shouldOpen));
        });

        document.body.classList.toggle('overflow-hidden', shouldOpen);
    };

    const closeSidebar = () => setOpen(false);

    menuButtons.forEach((button) => {
        button.addEventListener('click', () => {
            const isOpen = sidebar.classList.contains('translate-x-0');
            setOpen(!isOpen);
        });
    });

    backdrop?.addEventListener('click', closeSidebar);

    sidebar.querySelectorAll('a').forEach((link) => {
        link.addEventListener('click', () => {
            if (!desktopQuery.matches) {
                closeSidebar();
            }
        });
    });

    window.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            closeSidebar();
        }
    });

    const syncResponsiveState = () => closeSidebar();

    if (desktopQuery.addEventListener) {
        desktopQuery.addEventListener('change', syncResponsiveState);
    } else if (desktopQuery.addListener) {
        desktopQuery.addListener(syncResponsiveState);
    }

    syncResponsiveState();
})();
