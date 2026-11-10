(() => {
    const page = document.body.dataset.page;
    const toast = document.querySelector('#toast');
    const dialog = document.querySelector('#content-dialog');
    const dialogTitle = document.querySelector('#dialog-title');
    const dialogContent = document.querySelector('#dialog-content');
    let toastTimeout;
    let opener;
    let saved = new Set();
    let storageAvailable = true;
    try {
        const stored = JSON.parse(localStorage.getItem('bohan-saved-work') || '[]');
        if (Array.isArray(stored)) saved = new Set(stored.filter(value => typeof value === 'string'));
    } catch { storageAvailable = false; }

    function notify(message) {
        clearTimeout(toastTimeout);
        toast.textContent = message;
        toast.classList.add('is-visible');
        toastTimeout = setTimeout(() => toast.classList.remove('is-visible'), 3200);
    }

    function openDialog(title, trigger) {
        if (!dialog.open) opener = trigger;
        dialogTitle.textContent = title;
        dialogContent.replaceChildren();
        if (!dialog.open) dialog.showModal();
        document.body.style.overflow = 'hidden';
    }

    document.querySelector('#close-dialog').addEventListener('click', () => dialog.close());
    dialog.addEventListener('click', event => {
        const rect = dialog.getBoundingClientRect();
        if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) dialog.close();
    });
    dialog.addEventListener('close', () => {
        dialogContent.replaceChildren();
        document.body.style.overflow = '';
        opener?.focus({ preventScroll: true });
    });

    async function copyText(text, success) {
        try {
            await navigator.clipboard.writeText(text);
            notify(success);
        } catch {
            openDialog('Copy text', document.activeElement);
            const textarea = document.createElement('textarea');
            textarea.value = text;
            textarea.className = 'citation-text';
            textarea.style.width = '100%';
            textarea.rows = 5;
            textarea.readOnly = true;
            textarea.setAttribute('aria-label', 'Text to copy');
            dialogContent.append(textarea);
            textarea.focus();
            textarea.select();
            notify('Select and copy the text.');
        }
    }

    document.querySelectorAll('[data-image]').forEach(button => {
        button.addEventListener('click', () => {
            openDialog(button.dataset.imageTitle, button);
            const image = document.createElement('img');
            image.className = 'dialog-image';
            image.src = button.dataset.image;
            image.alt = button.dataset.imageTitle;
            dialogContent.append(image);
        });
    });

    document.querySelectorAll('[data-video]').forEach(button => {
        button.addEventListener('click', () => {
            openDialog(button.dataset.videoTitle, button);
            const frame = document.createElement('iframe');
            frame.src = button.dataset.video;
            frame.title = button.dataset.videoTitle;
            frame.className = 'video-embed';
            frame.allow = 'autoplay; encrypted-media; fullscreen; picture-in-picture';
            frame.allowFullscreen = true;
            frame.referrerPolicy = 'strict-origin-when-cross-origin';
            const link = document.createElement('a');
            link.href = button.dataset.videoUrl;
            link.target = '_blank';
            link.rel = 'noopener noreferrer';
            link.className = 'video-fallback';
            link.textContent = 'Open original video ↗';
            dialogContent.append(frame, link);
        });
    });

    document.querySelectorAll('[data-citation]').forEach(button => {
        button.addEventListener('click', () => {
            openDialog('BibTeX citation', button);
            const text = document.createElement('pre');
            text.className = 'citation-text';
            const code = document.createElement('code');
            code.textContent = button.dataset.citation;
            text.append(code);
            const copy = document.createElement('button');
            copy.className = 'button primary citation-copy';
            copy.textContent = 'Copy BibTeX';
            copy.addEventListener('click', () => copyText(button.dataset.citation, 'BibTeX copied.'));
            dialogContent.append(text, copy);
        });
    });

    document.querySelectorAll('[data-share]').forEach(button => {
        button.addEventListener('click', () => {
            const url = new URL(location.href);
            url.hash = button.dataset.share;
            url.search = '';
            copyText(url.href, 'Link copied.');
        });
    });

    const filterButtons = [...document.querySelectorAll('[data-filter]')];
    const search = document.querySelector('#work-search');
    const cards = [...document.querySelectorAll('[data-work]')];
    let currentFilter = 'all';

    function updateFilters() {
        filterButtons.forEach(button => {
            const active = button.dataset.filter === currentFilter;
            button.classList.toggle('is-active', active);
            button.setAttribute('aria-pressed', String(active));
        });
        if (page === 'research') {
            const query = (search?.value || '').toLocaleLowerCase().trim();
            let visible = 0;
            cards.forEach(card => {
                const matchesFilter = currentFilter === 'all' || currentFilter === card.dataset.kind || (currentFilter === 'saved' && saved.has(card.dataset.work));
                card.hidden = !(matchesFilter && card.textContent.toLocaleLowerCase().includes(query));
                if (!card.hidden) visible++;
            });
            document.querySelectorAll('.year-group').forEach(group => { group.hidden = ![...group.querySelectorAll('[data-work]')].some(card => !card.hidden); });
            document.querySelector('.empty-results').hidden = visible > 0;
            document.querySelector('.feed-end').hidden = visible === 0;
        }
        if (page === 'videos') {
            document.querySelectorAll('[data-video-category]').forEach(card => { card.hidden = currentFilter !== 'all' && card.dataset.videoCategory !== currentFilter; });
        }
    }

    function setFilter(filter) { currentFilter = filter; updateFilters(); }
    filterButtons.forEach(button => button.addEventListener('click', () => setFilter(button.dataset.filter)));
    search?.addEventListener('input', updateFilters);
    document.querySelector('#reset-filters')?.addEventListener('click', () => { search.value = ''; setFilter('all'); });

    const saveButtons = [...document.querySelectorAll('[data-save]')];
    function updateSaved() {
        saveButtons.forEach(button => {
            const active = saved.has(button.dataset.save);
            button.setAttribute('aria-pressed', String(active));
            const title = button.closest('article').querySelector('h3').textContent;
            button.setAttribute('aria-label', `${active ? 'Unsave' : 'Save'} ${title}`);
        });
    }
    saveButtons.forEach(button => button.addEventListener('click', () => {
        const id = button.dataset.save;
        const active = !saved.has(id);
        if (active) saved.add(id); else saved.delete(id);
        try {
            localStorage.setItem('bohan-saved-work', JSON.stringify([...saved]));
            storageAvailable = true;
        }
        catch { storageAvailable = false; }
        updateSaved();
        updateFilters();
        notify(active ? (storageAvailable ? 'Saved on this device.' : 'Saved for this visit.') : 'Removed from saved work.');
    }));
    updateSaved();

    function legacyAnchor() {
        const hash = location.hash;
        if (page !== 'research') return;
        if (hash === '#about' || hash === '#research') { location.replace(`about.html${hash}`); return; }
        if (hash === '#demos') { location.replace('videos.html'); return; }
        if (hash === '#projects' || hash === '#publications') {
            setFilter(hash === '#projects' ? 'project' : 'paper');
            document.querySelector('#main-content').scrollIntoView();
        }
    }
    legacyAnchor();
    window.addEventListener('hashchange', legacyAnchor);
})();
