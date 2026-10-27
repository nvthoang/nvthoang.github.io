/* Progressive enhancement: all pages, publication records and forms are HTML. */
'use strict';
(() => {
  document.documentElement.classList.add('js');
  const menu = document.querySelector('.menu-toggle');
  const nav = document.querySelector('#primary-nav');
  if (menu && nav) {
    const closeMenu = () => {menu.setAttribute('aria-expanded', 'false'); nav.classList.remove('is-open');};
    menu.addEventListener('click', () => {
      const open = menu.getAttribute('aria-expanded') !== 'true';
      menu.setAttribute('aria-expanded', String(open)); nav.classList.toggle('is-open', open);
    });
    document.addEventListener('keydown', e => {if (e.key === 'Escape' && menu.getAttribute('aria-expanded') === 'true') {closeMenu(); menu.focus();}});
    document.addEventListener('click', e => {if (!e.target.closest('.site-header')) closeMenu();});
    window.matchMedia('(min-width: 901px)').addEventListener('change', closeMenu);
  }

  let noticeTimer;
  function notice(text) {
    const el = document.querySelector('#site-notice');
    if (!el) return;
    el.textContent = text; el.hidden = false;
    window.clearTimeout(noticeTimer);
    noticeTimer = window.setTimeout(() => {el.hidden = true;}, 6500);
  }

  // Free whole-page translation. No API key, scraping endpoint or browser secret.
  // Source is server-rendered HTML, so Google can translate newly published news.
  const vi = document.querySelector('.language-vi');
  const en = document.querySelector('.language-en');
  const canonical = document.querySelector('link[rel="canonical"]')?.href;
  const current = new URL(window.location.href);
  const translated = current.hostname.endsWith('.translate.goog');
  const privatePreview = current.protocol === 'file:' || current.hostname === 'localhost' || current.hostname === '127.0.0.1' || current.hostname.endsWith('.local') || current.hostname.endsWith('.localhost');
  const original = translated && canonical ? canonical : current.href;
  // All metadata excludes form values. Query parameters may select the enquiry topic.
  const translationURL = new URL('https://translate.google.com/translate');
  translationURL.searchParams.set('sl', 'en');
  translationURL.searchParams.set('tl', 'vi');
  translationURL.searchParams.set('u', original);
  if (vi) {
    vi.href = translationURL.href;
    if (translated) {vi.setAttribute('aria-current','true'); en?.removeAttribute('aria-current');}
    vi.addEventListener('click', e => {
      if (privatePreview) {
        e.preventDefault();
        notice('Vietnamese translation needs a publicly accessible website. After deployment, VI opens this page in Google Translate.');
      }
    });
  }
  if (en) {
    en.href = translated && canonical ? canonical : current.href;
    if (!translated) en.setAttribute('aria-current', 'true');
  }

  const filters = document.querySelector('#publication-filters');
  if (filters) {
    const search = document.querySelector('#pub-search');
    const year = document.querySelector('#pub-year');
    const topic = document.querySelector('#pub-topic');
    const type = document.querySelector('#pub-type');
    const records = [...document.querySelectorAll('#publication-list .publication')].map(el => ({
      el, text:el.textContent.toLocaleLowerCase(), year:el.dataset.year,
      topics:JSON.parse(el.dataset.topics), type:el.dataset.type
    }));
    const count = document.querySelector('#pub-count');
    const empty = document.querySelector('#pub-empty');
    const update = () => {
      const terms = search.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
      let total = 0;
      records.forEach(r => {
        const visible = terms.every(term => (r.text+' '+r.topics.join(' ').toLocaleLowerCase()).includes(term)) && (!year.value || r.year === year.value) && (!topic.value || r.topics.includes(topic.value)) && (!type.value || r.type === type.value);
        r.el.hidden = !visible;
        total += Number(visible);
      });
      count.textContent = `Showing ${total} of ${records.length} publications`;
      empty.hidden = total !== 0;
    };
    filters.addEventListener('input', update);
    filters.addEventListener('change', update);
    filters.addEventListener('submit', e => e.preventDefault());
    filters.addEventListener('reset', () => window.setTimeout(update,0));
  }

  document.querySelectorAll('.copy-citation').forEach(button => {
    button.addEventListener('click', async () => {
      try {
        if (!navigator.clipboard) throw new Error('Clipboard unavailable');
        await navigator.clipboard.writeText(button.dataset.citation);
        notice('Citation copied.');
      } catch (_) {
        // Read-only selectable fallback works without clipboard permissions.
        const text = document.createElement('textarea');
        text.value = button.dataset.citation;
        text.setAttribute('readonly','');
        text.setAttribute('aria-label','Citation — select and copy');
        text.className='citation-fallback';
        button.parentElement.append(text); text.focus(); text.select();
        notice('Select and copy the citation below the button.');
        text.addEventListener('blur', () => text.remove(), {once:true});
      }
    });
  });

  const contact = document.querySelector('.contact-form');
  if (contact) {
    const topic = document.querySelector('#contact-topic');
    const requested = current.searchParams.get('topic');
    if ([...topic.options].some(option => option.value === requested)) topic.value = requested;
    // Native POST preserves FormSubmit's CAPTCHA, error and activation screens.
    // Do not show a simulated "delivered" message or store contact data locally.
    contact.addEventListener('submit', () => {
      document.querySelector('.form-status').textContent = 'Continuing to the secure form service. Complete any spam check shown there.';
    });
  }
})();
