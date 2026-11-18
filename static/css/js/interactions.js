document.addEventListener('DOMContentLoaded', () => {
    let toastRegion;

    function notify(message, level = 'info', anchor = null) {
        if (!toastRegion) {
            toastRegion = document.createElement('div');
            toastRegion.className = 'app-notification-region';
            toastRegion.setAttribute('aria-live', 'polite');
            toastRegion.setAttribute('aria-atomic', 'true');
            document.body.appendChild(toastRegion);
        }

        const toast = document.createElement('div');
        toast.className = `app-notification app-notification-${level}`;
        toast.setAttribute('role', 'status');
        toast.textContent = message;
        anchor = anchor || document.querySelector('#notificationButton, .topbar, .main-header');
        if (anchor) {
            const rect = anchor.getBoundingClientRect();
            const width = Math.min(350, window.innerWidth - 24);
            const left = Math.max(width / 2 + 12, Math.min(rect.left + rect.width / 2, window.innerWidth - width / 2 - 12));
            const below = rect.top < 110;
            toast.style.width = `${width}px`;
            toast.style.left = `${left}px`;
            toast.style.top = `${below ? rect.bottom + 8 : rect.top - 8}px`;
            toast.classList.toggle('is-below', below);
        }
        toastRegion.appendChild(toast);

        requestAnimationFrame(() => toast.classList.add('is-visible'));
        window.setTimeout(() => {
            toast.classList.remove('is-visible');
            window.setTimeout(() => toast.remove(), 250);
        }, 3600);
    }

    window.showAppNotification = notify;

    // The top bar bell repeats current Django messages or explains that none are waiting.
    const notificationButton = document.getElementById('notificationButton');
    const pageAlerts = [...document.querySelectorAll('.content-area .alert')]
        .map(alert => alert.innerText.trim())
        .filter(Boolean);

    if (pageAlerts.length) {
        const messages = pageAlerts.slice(0, 3).join(' · ');
        window.setTimeout(() => notify(messages, 'info', notificationButton), 120);
    } else {
        try {
            const pendingMessage = sessionStorage.getItem('appPendingNotification');
            if (pendingMessage) {
                sessionStorage.removeItem('appPendingNotification');
                window.setTimeout(() => notify(pendingMessage), 120);
            }
        } catch (error) {
            // Notifications still work when the browser blocks session storage.
        }
    }

    if (notificationButton) {
        notificationButton.addEventListener('click', () => {
            const alerts = [...document.querySelectorAll('.content-area .alert')]
                .map(alert => alert.innerText.trim())
                .filter(Boolean);
            if (alerts.length) {
                const messages = alerts.slice(0, 3).join(' · ');
                notify(alerts.length > 3 ? `${messages} · ${alerts.length - 3} more` : messages, 'info', notificationButton);
            } else {
                notify('You have no new notifications.', 'info', notificationButton);
            }
        });
    }

    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', () => {
            const isOpen = window.innerWidth <= 768
                ? sidebar.classList.contains('show')
                : !sidebar.classList.contains('collapsed');
            notify(isOpen ? 'Navigation menu opened.' : 'Navigation menu collapsed.', 'info', sidebarToggle);
        });
    }

    // Search table rows on the current page and report the number of matches.
    const searchInput = document.getElementById('pageSearchInput');
    const searchButton = document.getElementById('pageSearchButton');
    if (searchInput) {
        const filterRows = (announce = false) => {
            const query = searchInput.value.trim().toLocaleLowerCase();
            const rows = [...document.querySelectorAll('.content-area table tbody tr')]
                .filter(row => !row.querySelector('[colspan]'));

            rows.forEach(row => {
                row.hidden = Boolean(query) && !row.innerText.toLocaleLowerCase().includes(query);
            });

            if (announce) {
                const visibleCount = rows.filter(row => !row.hidden).length;
                notify(query ? `${visibleCount} matching row${visibleCount === 1 ? '' : 's'} found on this page.` : 'Search cleared. All rows are visible.', 'info', searchButton || searchInput);
            }
        };

        searchInput.addEventListener('input', () => filterRows(false));
        searchInput.addEventListener('keydown', event => {
            if (event.key === 'Enter') {
                event.preventDefault();
                filterRows(true);
            }
        });
        searchButton?.addEventListener('click', () => {
            if (!searchInput.value.trim()) searchInput.focus();
            filterRows(true);
        });
    }

    // Icons inside links and buttons inherit those controls' actions. Standalone icons
    // become keyboard accessible and announce the content they represent when activated.
    document.querySelectorAll('i.bi').forEach(icon => {
        const owner = icon.closest('a, button, [role="button"]');
        if (owner) {
            icon.classList.add('icon-action');
            if (owner.tagName === 'BUTTON' && owner.type === 'button') return;
            icon.addEventListener('click', () => {
                const action = (owner.getAttribute('aria-label') || owner.title || owner.innerText || 'Action')
                    .replace(/\s+/g, ' ')
                    .trim()
                    .slice(0, 100);
                const message = `${action} activated.`;
                notify(message, 'info', icon);
                if (owner.tagName === 'A' || owner.type === 'submit') {
                    try {
                        sessionStorage.setItem('appPendingNotification', message);
                    } catch (error) {
                        // The current-page notification remains visible when storage is blocked.
                    }
                }
            });
            return;
        }

        const context = icon.closest('h1, h2, h3, h4, h5, td, th, .card, .alert, .badge, .stat-card')
            || icon.parentElement;
        const description = (context?.innerText || context?.textContent || 'Information')
            .replace(/\s+/g, ' ')
            .trim()
            .slice(0, 150);

        icon.classList.add('interactive-icon');
        icon.setAttribute('role', 'button');
        icon.setAttribute('tabindex', '0');
        icon.setAttribute('aria-label', description ? `Show information: ${description}` : 'Show information');
        icon.setAttribute('title', description || 'Show information');

        const activate = () => notify(description || 'This icon represents information on the current page.', 'info', icon);
        icon.addEventListener('click', activate);
        icon.addEventListener('keydown', event => {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                activate();
            }
        });
    });

    // Give form buttons immediate feedback and prevent accidental double submits.
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) return;
            const button = event.submitter || form.querySelector('button[type="submit"], button:not([type])');
            if (!button || button.disabled) return;

            button.disabled = true;
            button.classList.add('is-loading');
            button.setAttribute('aria-busy', 'true');
            const label = button.innerText.toLowerCase();
            const progress = label.includes('delete') ? 'Deleting...' : label.includes('logout') ? 'Signing out...' : 'Working...';
            button.dataset.progressLabel = progress;
            notify(progress, 'info', button);
            try {
                sessionStorage.setItem('appPendingNotification', progress);
            } catch (error) {
                // The current-page popup remains available when storage is blocked.
            }
            const spinner = document.createElement('span');
            spinner.className = 'button-spinner';
            spinner.setAttribute('aria-hidden', 'true');
            button.prepend(spinner);
            button.append(` ${progress}`);
        });
    });

    // Accessible feedback for non-submit buttons, including the navigation toggle.
    document.querySelectorAll('button[type="button"], button:not([type])').forEach(button => {
        if (button.id === 'notificationButton' || button.id === 'pageSearchButton' || button.id === 'sidebarToggle') return;
        button.addEventListener('click', () => {
            if (button.hasAttribute('data-bs-dismiss')) notify('Message dismissed.', 'info', button);
            else notify(`${button.innerText.trim() || 'Button'} activated.`, 'info', button);
        });
    });
});
