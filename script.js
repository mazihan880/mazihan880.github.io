document.documentElement.classList.add('enhanced');

const body = document.body;
const menuToggle = document.querySelector('.menu-toggle');
const navLinks = [...document.querySelectorAll('.nav-links a')];
const filterButtons = [...document.querySelectorAll('[data-filter]')];
const publications = [...document.querySelectorAll('.pub-card')];
const progressBar = document.querySelector('.scroll-progress span');
const emailLinks = [...document.querySelectorAll('[data-copy-email]')];

async function copyToClipboard(value) {
    if (navigator.clipboard && window.isSecureContext) {
        try {
            await navigator.clipboard.writeText(value);
            return;
        } catch (error) {
            // Fall through to the selection-based copy method.
        }
    }

    const input = document.createElement('textarea');
    input.value = value;
    input.setAttribute('readonly', '');
    input.style.position = 'fixed';
    input.style.opacity = '0';
    document.body.appendChild(input);
    input.select();
    input.setSelectionRange(0, input.value.length);
    const copied = document.execCommand('copy');
    input.remove();
    if (!copied) throw new Error('Clipboard copy failed');
}

emailLinks.forEach((link) => {
    let resetTimer;
    link.addEventListener('click', async (event) => {
        event.preventDefault();
        const feedback = link.querySelector('[data-copy-feedback]');

        try {
            await copyToClipboard(link.dataset.copyEmail);
            window.clearTimeout(resetTimer);
            link.classList.add('is-copied');
            if (feedback) feedback.textContent = feedback.dataset.copiedText || 'Copied ✓';

            resetTimer = window.setTimeout(() => {
                link.classList.remove('is-copied');
                if (feedback) feedback.textContent = feedback.dataset.defaultText || '↗';
            }, 2200);
        } catch (error) {
            window.location.href = link.href;
        }
    });
});

menuToggle?.addEventListener('click', () => {
    const open = body.classList.toggle('nav-open');
    menuToggle.setAttribute('aria-expanded', String(open));
    menuToggle.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
});

navLinks.forEach((link) => {
    link.addEventListener('click', () => {
        body.classList.remove('nav-open');
        menuToggle?.setAttribute('aria-expanded', 'false');
        menuToggle?.setAttribute('aria-label', 'Open navigation');
    });
});

filterButtons.forEach((button) => {
    button.addEventListener('click', () => {
        const filter = button.dataset.filter;
        filterButtons.forEach((item) => {
            const active = item === button;
            item.classList.toggle('is-active', active);
            item.setAttribute('aria-pressed', String(active));
        });

        publications.forEach((publication) => {
            const visible = filter === 'all' || publication.dataset.topic === filter;
            publication.hidden = !visible;
        });
    });
});

const revealObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach((entry) => {
        if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            observer.unobserve(entry.target);
        }
    });
}, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });

document.querySelectorAll('.reveal').forEach((element) => revealObserver.observe(element));

const sections = [...document.querySelectorAll('main section[id], main header[id]')];
const sectionObserver = new IntersectionObserver((entries) => {
    const visible = entries
        .filter((entry) => entry.isIntersecting)
        .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];

    if (!visible) return;
    navLinks.forEach((link) => {
        link.classList.toggle('is-active', link.getAttribute('href') === `#${visible.target.id}`);
    });
}, { rootMargin: '-28% 0px -58% 0px', threshold: [0, 0.1, 0.4] });

sections.forEach((section) => sectionObserver.observe(section));

function updateProgress() {
    const scrollable = document.documentElement.scrollHeight - window.innerHeight;
    const progress = scrollable > 0 ? window.scrollY / scrollable : 0;
    progressBar.style.transform = `scaleX(${Math.min(1, Math.max(0, progress))})`;
}

window.addEventListener('scroll', updateProgress, { passive: true });
window.addEventListener('resize', updateProgress);
updateProgress();

function normalizeTitle(title) {
    return title
        .normalize('NFKD')
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, ' ')
        .trim();
}

function formatCompact(value) {
    return new Intl.NumberFormat('en', {
        notation: value >= 1000 ? 'compact' : 'standard',
        maximumFractionDigits: 1
    }).format(value);
}

async function updateScholarCitations() {
    try {
        const response = await fetch('data/scholar.json', { cache: 'no-store' });
        if (!response.ok) return;
        const snapshot = await response.json();
        const papers = new Map(
            (snapshot.papers || []).map((paper) => [normalizeTitle(paper.title), paper])
        );

        document.querySelectorAll('[data-citation]').forEach((element) => {
            const paper = papers.get(normalizeTitle(element.dataset.scholarTitle || ''));
            if (!paper) return;
            element.textContent = `Cited by ${paper.citations || 0}`;
            if (paper.scholar_url) element.href = paper.scholar_url;
        });

    } catch (error) {
        // The static fallback values remain visible when Scholar data is unavailable.
    }
}

async function fetchGitHubStars(repository) {
    const response = await fetch(`https://img.shields.io/github/stars/${repository}.json`, { cache: 'no-store' });
    if (!response.ok) throw new Error('GitHub stats unavailable');
    const data = await response.json();
    const raw = String(data.value ?? data.message ?? '').trim().toLowerCase();
    const match = raw.match(/^(\d+(?:\.\d+)?)(k|m)?$/);
    if (!match) throw new Error('Unexpected GitHub stats format');
    const multiplier = match[2] === 'm' ? 1_000_000 : match[2] === 'k' ? 1_000 : 1;
    return Math.round(Number(match[1]) * multiplier);
}

async function fetchHuggingFaceDownloads(dataset) {
    const response = await fetch(`https://huggingface.co/api/datasets/${dataset}`, { cache: 'no-store' });
    if (!response.ok) throw new Error('Hugging Face stats unavailable');
    const data = await response.json();
    return Number(data.downloads || 0);
}

async function updateLiveStats() {
    document.querySelectorAll('[data-github-repo]').forEach(async (element) => {
        try {
            const stars = await fetchGitHubStars(element.dataset.githubRepo);
            element.textContent = `GitHub stars · ${formatCompact(stars)}`;
        } catch (error) {
            element.textContent = 'GitHub stars · live';
        }
    });

    document.querySelectorAll('[data-hf-datasets]').forEach(async (element) => {
        try {
            const datasets = element.dataset.hfDatasets.split(',').map((item) => item.trim()).filter(Boolean);
            const downloads = await Promise.all(datasets.map(fetchHuggingFaceDownloads));
            const total = downloads.reduce((sum, count) => sum + count, 0);
            element.textContent = `HF downloads · ${formatCompact(total)}`;
        } catch (error) {
            element.textContent = 'HF downloads · live';
        }
    });
}

updateScholarCitations();
updateLiveStats();

document.getElementById('current-year').textContent = new Date().getFullYear();
