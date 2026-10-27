#!/usr/bin/env python3
"""Generate a complete static academic website using only Python 3.11+."""
from pathlib import Path
from html import escape, unescape
from urllib.parse import urlsplit, quote
from datetime import datetime, timezone
import argparse
import json
import re
import shutil
import sys
import xml.etree.ElementTree as ET
from bibtex import publications, BibTeXError

ROOT = Path(__file__).resolve().parents[1]
NAV = [('index.html','Home'),('about.html','About'),('research.html','Research'),('projects.html','Projects'),
       ('publications.html','Publications'),('people.html','People'),('news.html','News'),('resources.html','Teaching & Resources')]
SVG_PATHS = [
    '<path d="M5 19V9m7 10V5m7 14v-7M3 21h19"/>',
    '<path d="M6 6l12 3-6 11L6 6l14 11M6 6l-3 9 9 5 8-3-2-8"/><circle cx="6" cy="6" r="2"/><circle cx="18" cy="9" r="2"/><circle cx="12" cy="20" r="2"/>',
    '<path d="M6 3c0 8 12 10 12 18M18 3C18 11 6 13 6 21M7 5h10M9 9h6M9 15h6M7 19h10"/>',
    '<path d="M3 12h5l3-7 3 14 3-7h4M5 4h14a2 2 0 0 1 2 2v14H3V6a2 2 0 0 1 2-2z"/>',
    '<path d="M12 3l8 5v9l-8 4-8-4V8l8-5zm0 0v9m8-4-8 4-8-4m8 4v9"/>'
]


def h(value):
    return escape(str(value), quote=True)


def safe_url(value):
    value = str(value).strip()
    if not value:
        return ''
    if any(ord(c) < 32 for c in value) or '\\' in value:
        raise ValueError('Invalid URL: ' + value)
    parts = urlsplit(value)
    if parts.scheme:
        if parts.scheme not in {'https','http','mailto'}:
            raise ValueError('Unsupported URL scheme: ' + value)
    elif value.startswith('//') or '..' in Path(parts.path).parts or value.startswith('/'):
        raise ValueError('Use a relative local path or a full HTTPS URL: ' + value)
    return h(value)


def link(url, label, cls='', external=False):
    return f'<a href="{safe_url(url)}" class="{h(cls)}"'+(' target="_blank" rel="noopener noreferrer"' if external else '')+f'>{label}</a>'



def orcid_link(value, name):
    if not value:
        return ''
    identifier = str(value).strip().removeprefix('https://orcid.org/').rstrip('/')
    if not re.fullmatch(r'\d{4}-\d{4}-\d{4}-\d{3}[\dX]', identifier):
        raise ValueError('Invalid ORCID for ' + name)
    return (' <a class="orcid-link" href="https://orcid.org/' + identifier
            + '" target="_blank" rel="noopener noreferrer" aria-label="' + h(name)
            + ' — ORCID" title="ORCID"><svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true">'
            + '<circle cx="12" cy="12" r="12" fill="#A6CE39"/>'
            + '<g fill="#fff"><circle cx="6.4" cy="6.5" r="1.1"/>'
            + '<path d="M5.5 9h1.8v9H5.5zM9.5 5.5h4.1a6.25 6.25 0 0 1 0 12.5H9.5zm1.8 1.7v9.1h2.3a4.55 4.55 0 0 0 0-9.1z"/></g></svg></a>')


def icon(index):
    return '<svg class="area-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'+SVG_PATHS[index % 5]+'</svg>'


def inline(text):
    text = h(text)
    def md_link(m):
        from html import unescape
        return link(unescape(m[2]), m[1])
    text = re.sub(r'\[([^\]]+)\]\(([^\s)]+)\)', md_link, text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>',text)
    text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>',text)
    return text


def markdown(text):
    chunks, paragraph, bullets = [], [], []
    def flush():
        if paragraph:
            chunks.append('<p>'+inline(' '.join(paragraph))+'</p>'); paragraph.clear()
        if bullets:
            chunks.append('<ul>'+''.join('<li>'+inline(t)+'</li>' for t in bullets)+'</ul>'); bullets.clear()
    for line in text.splitlines():
        if not line.strip(): flush()
        elif line.startswith(('## ', '### ')):
            flush(); level = 3 if line.startswith('### ') else 2
            chunks.append(f'<h{level}>'+inline(line[level+1:])+f'</h{level}>')
        elif line.startswith('- '):
            if paragraph: flush()
            bullets.append(line[2:])
        else:
            if bullets: flush()
            paragraph.append(line.strip())
    flush()
    return ''.join(chunks)


def news_items():
    result = []
    for p in sorted((ROOT/'content/news').glob('*.md')):
        text = p.read_text(encoding='utf-8')
        if not text.startswith('---\n') or '\n---\n' not in text[4:]:
            raise ValueError(f'{p.name}: expected front matter between --- lines')
        front, body = text[4:].split('\n---\n',1)
        meta = {}
        for line in front.splitlines():
            if line.strip():
                key, value = line.split(':',1)
                meta[key.strip()] = value.strip()
        if meta.get('published','true') == 'false': continue
        for field in ('title','date','category'):
            if not meta.get(field): raise ValueError(f'{p.name}: missing {field}')
        if not re.fullmatch(r'\d{4}(?:-\d{2})?(?:-\d{2})?',meta['date']):
            raise ValueError(f'{p.name}: date must be YYYY, YYYY-MM or YYYY-MM-DD')
        datetime.strptime(meta['date'], {4:'%Y',7:'%Y-%m',10:'%Y-%m-%d'}[len(meta['date'])])
        result.append(dict(meta, body=markdown(body), slug=p.stem, filename=p.name))
    return sorted(result,key=lambda n:(n['date'],n['filename']),reverse=True)


def pub_url(pub):
    return 'https://doi.org/'+quote(pub['doi'], safe='/():;.') if pub['doi'] else pub.get('url','')


def citation(pub, compact=False):
    url = pub_url(pub)
    title = link(url,h(pub['title']),external=True) if url else h(pub['title'])
    authors = h(pub['authors']).replace('Thanh-Hoang Nguyen-Vo','<strong class="notranslate" translate="no">Thanh-Hoang Nguyen-Vo</strong>')
    tag = 'Journal article' if pub['entry_type']=='article' else 'Conference paper' if pub['entry_type']=='inproceedings' else 'Book / chapter'
    topics = pub['topics'] or ['Uncategorised']
    volume = pub.get('volume','') + ('('+pub['number']+')' if pub.get('number') else '')
    details = ' · '.join(filter(None,[str(pub['year']),volume,pub.get('pages','').replace('--','–')]))
    attrs = f'data-year="{pub["year"]}" data-type="{h(tag)}" data-topics="{h(json.dumps(topics))}"'
    return f'''<article class="publication {'compact' if compact else ''}" id="{h(pub['key'])}" {attrs}>
      <div class="pub-marker">{pub['year']}<span>{h(tag)}</span></div>
      <div class="pub-content"><h3 class="notranslate" translate="no">{title}</h3>
      <p class="authors notranslate" translate="no">{authors}</p>
      <p class="venue notranslate" translate="no">{h(pub['venue'])} <span>· {h(details)}</span></p>
      <div class="pub-actions">{link(url,'Read publication <span aria-hidden="true">↗</span>',external=True) if url else ''}
      <button type="button" class="text-button copy-citation" data-citation="{h(pub['authors']+'. ('+str(pub['year'])+'). '+pub['title']+'. '+pub['venue']+'. '+url)}">Copy citation</button></div></div></article>'''


def news_card(item):
    return f'''<article class="news-card"><div class="meta"><time datetime="{h(item['date'])}">{h(item['date'])}</time><span>{h(item['category'])}</span></div>
    <h3>{link('news/'+item['slug']+'.html',h(item['title']))}</h3><p>{h(unescape(re.sub('<[^>]+>','',item['body'].split('</p>')[0])))}</p>
    {link('news/'+item['slug']+'.html','Read update <span aria-hidden="true">↗</span>','text-link')}</article>'''


def section_head(kicker,title,description='',url='',label='View all'):
    return f'<div class="section-heading"><div><p class="eyebrow">{h(kicker)}</p><h2>{title}</h2>{"<p>"+h(description)+"</p>" if description else ""}</div>{link(url,h(label)+" <span aria-hidden=\"true\">↗</span>","text-link") if url else ""}</div>'


def page_intro(kicker,title,text,wide=False):
    label = f'<p class="eyebrow">{h(kicker)}</p>' if kicker.casefold()!=title.casefold() else ''
    extra = ' wide-intro' if wide else ''
    return f'<section class="page-intro container{extra}">{label}<h1>{title}</h1><p class="lead">{h(text)}</p></section>'


def callout():
    return '<section class="collab container"><div><p class="eyebrow">Let’s connect</p><h2>A shared question is<br>a good place to start.</h2><p>Students, researchers and collaborators are welcome to get in touch.</p></div>'+link('join.html','Explore opportunities <span aria-hidden="true">↗</span>','button light')+'</section>'


def render(config, title, content, filename, description='', prefix='', active=''):
    template = (ROOT/'templates/base.html').read_text(encoding='utf-8')
    nav = ''.join(f'<a href="{path}"'+(' aria-current="page"' if path==(active or filename) else '')+f'>{h(label)}</a>' for path,label in NAV)
    canonical = config['site_url'].rstrip('/')+'/'+('' if filename=='index.html' else filename)
    schema = json.dumps({'@context':'https://schema.org','@type':'Person','name':config['name'],'alternateName':config['published_name'],'url':config['site_url'],
                         'sameAs':[config['scholar'],config['orcid'],config['github']],'knowsAbout':[r['name'] for r in config['research']]},ensure_ascii=False).replace('<','\\u003c')
    replacements = {'TITLE':h(title+' | '+config['group']) if title!='Home' else h(config['name']+' | Data Science & AI Research'),
        'DESCRIPTION':h(description or config['description']),'CANONICAL':safe_url(canonical),'NAV':nav,'CONTENT':content,'SCHEMA':schema,
        'YEAR':str(datetime.now(timezone.utc).year),'GROUP':h(config['group']),'EMAIL':h(config['email']),
        'SCHOLAR':safe_url(config['scholar']),'ORCID':safe_url(config['orcid']),'GITHUB':safe_url(config['github']),
        'PAGE':h(filename),'PREFIX':prefix,'OG_IMAGE':safe_url(config['site_url'].rstrip('/')+'/assets/logo.png')}
    for key,value in replacements.items():
        template = template.replace('{{'+key+'}}',value)
    if filename=='contact.html':
        template = template.replace('class="nav-contact" href="contact.html"','class="nav-contact" href="contact.html" aria-current="page"')
    if filename=='join.html':
        template = template.replace('href="join.html" class="join-link"','href="join.html" class="join-link" aria-current="page"')
    # All generated links/assets are relative to the root; nested news gets a base URL.
    return template


def build(output):
    c = json.loads((ROOT/'content/site.json').read_text(encoding='utf-8'))
    if len(c['research']) != 5:
        raise ValueError('The initial design expects five main research directions; edit the layout to change this.')
    pubs = publications((ROOT/'content/publications.bib').read_text(encoding='utf-8'))
    lookup = {p['key']:p for p in pubs}
    news = news_items()
    for key in c['featured_publications']:
        if key not in lookup: raise ValueError('Unknown featured publication key: '+key)
    for n in news:
        if n.get('publication') and n['publication'] not in lookup:
            raise ValueError(n['filename']+': unknown publication key '+n['publication'])
    people = [p for p in c['people'] if p.get('published',True)]
    for p in people:
        if p['role'] not in {'Senior Researcher','Researcher','Research Assistant'}:
            raise ValueError('People role must be Senior Researcher, Researcher or Research Assistant: '+p['name'])
    # Build only into the fixed generated directory to avoid accidental source deletion.
    if output.resolve() != (ROOT/'dist').resolve():
        raise ValueError('Output must be the project dist directory')
    output.mkdir(parents=True,exist_ok=True)
    # Preserve the directory inode for static preview servers already serving it.
    for child in output.iterdir():
        if child.is_dir() and not child.is_symlink(): shutil.rmtree(child)
        else: child.unlink()
    shutil.copytree(ROOT/'assets',output/'assets')
    # Export only the records visible on the website, never excluded preprints.
    bibliography = ['% Published records displayed on this website.\n']
    for p in pubs:
        fields = {k:v for k,v in p.items() if k not in {'key','entry_type','authors','venue','topics','crossref'} and not isinstance(v,list)}
        bibliography.append('@'+p['entry_type']+'{'+p['key']+',\n'+''.join('  '+k+'={'+str(v)+'},\n' for k,v in fields.items())+'}\n')
    (output/'assets/publications.bib').write_text('\n'.join(bibliography),encoding='utf-8')
    (output/'news').mkdir()
    pages = {}
    directions = ''.join(link('research.html#'+r['id'],f'<span class="direction-number">{i+1}</span>{h(r["name"])}<span aria-hidden="true">↗</span>') for i,r in enumerate(c['research']))
    rows = ''.join(f'<a class="research-row" href="research.html#{r["id"]}"><span class="row-number">{i+1}</span>{icon(i)}<div><h3>{h(r["name"])}</h3><p>{h(r["short"])}</p></div><span class="row-arrow" aria-hidden="true">↗</span></a>' for i,r in enumerate(c['research']))
    featured_news = [n for n in news if n.get('featured')=='true'] or news[:2]
    pages['index.html'] = ('Home',f'''
    <section class="hero container"><div class="hero-copy"><p class="eyebrow"><span class="status-dot"></span> Wellington, New Zealand</p>
    <h1><span>Data. Intelligence.<br>Scientific discovery.</span></h1><p class="lead">{h(c['intro'])}</p>
    <div class="hero-actions">{link('research.html','Explore the research <span aria-hidden="true">↗</span>','button')}{link('contact.html','Start a conversation','text-link')}</div>
    <p class="published-name">Publishing as <span class="notranslate" translate="no">{h(c['published_name'])}</span></p></div>
    <aside class="hero-identity" aria-label="Hoang Nguyen Research Group"><div class="identity-top"><span>RESEARCH GROUP</span><span aria-hidden="true">↗</span></div>
    <img src="assets/logo.webp" width="760" height="760" alt="THNV — Hoang Nguyen Research Group emblem" fetchpriority="high">
    <div class="identity-bottom"><span>Led by Hoang Nguyen</span></div></aside></section>
    <div class="directions-strip container">{directions}</div>
    <section class="section container">{section_head('Research highlights','Recent published work',url='publications.html',label='Publication library')}
    <div class="highlight-list">{''.join(citation(lookup[k],True) for k in c['featured_publications'])}</div></section>
    <section class="research-home"><div class="container research-split"><div class="research-editorial"><p class="eyebrow">Research directions</p><h2>Methods that connect.<br>Questions that matter.</h2><p>Five main directions connect our computational work with biology, healthcare and drug discovery. Our interests extend to related questions across disciplines.</p>{link('research.html','Find a shared interest <span aria-hidden="true">↗</span>','text-link')}</div><div class="research-rows">{rows}</div></div></section>
    <section class="section container">{section_head('From the group','Notes & updates.',url='news.html',label='All updates')}<div class="news-grid">{''.join(news_card(n) for n in featured_news[:2])}</div></section>
    {callout()}''')

    cv = link(c['cv_file'],'Download CV <span aria-hidden="true">↓</span>','button secondary') if c.get('cv_file') else ''
    about_text = ''.join('<p>'+h(p)+'</p>' for p in c['about'])
    pages['about.html'] = ('About',page_intro('About','About','Research across data science, artificial intelligence and the life sciences.')+f'''
    <section class="container about-grid section-bottom"><aside class="profile-panel"><img src="assets/logo.webp" width="360" height="360" alt="Hoang Nguyen Research Group emblem"><h2 class="notranslate" translate="no">Hoang Nguyen</h2><p>Group Lead</p>{cv}</aside><div class="prose"><h2>Research & background</h2>{about_text}
    <h3>Research identity</h3><p>My publications appear under <strong class="notranslate" translate="no">{h(c['published_name'])}</strong>. Use the links below to find my academic profiles and published work.</p><div class="profile-links">{link(c['scholar'],'Google Scholar ↗',external=True)}{link(c['orcid'],'ORCID ↗',external=True)}{link(c['github'],'GitHub ↗',external=True)}</div>
    </div></section>{callout()}''')

    areas = ''.join(f'''<article class="research-detail" id="{r['id']}"><div class="research-detail-label"><span class="row-number">{i+1}</span>{icon(i)}</div><div><h2>{h(r['name'])}</h2><p class="lead-small">{h(r['description'])}</p><div class="tags">{''.join('<span>'+h(t)+'</span>' for t in r['topics'])}</div><div class="collaboration-note"><h3>Where we could work together</h3><p>{h(r['collaboration'])}</p></div></div></article>''' for i,r in enumerate(c['research']))
    pages['research.html'] = ('Research',page_intro('Research','Research','Our main research directions overlap. We welcome related questions that connect methods, data and meaningful applications.',wide=True)+f'<section class="container section-bottom">{areas}</section>'+callout())

    projects = [p for p in c['projects'] if p.get('published',True)]
    project_cards = ''.join(f'''<article class="project-card"><div class="meta"><span>{h(p['area'])}</span><span aria-hidden="true">0{i+1}</span></div><div class="project-sketch" aria-hidden="true">{icon(i)}</div><span class="badge">{h(p['status'])}</span><h2>{h(p['title'])}</h2><p>{h(p['description'])}</p>{link(p['url'],'Explore project ↗','text-link',True) if p.get('url') else ''}</article>''' for i,p in enumerate(projects))
    pages['projects.html'] = ('Projects',page_intro('Projects','Projects','Projects are coordinated by Hoang Nguyen. Public project descriptions and links to published outputs will be added here.',wide=True)+f'<section class="container section-bottom"><div class="projects-grid">{project_cards}</div></section>'+callout())

    years = sorted({p['year'] for p in pubs},reverse=True)
    topics = sorted({t for p in pubs for t in (p['topics'] or ['Uncategorised'])})
    options = lambda values: ''.join(f'<option value="{h(v)}">{h(v)}</option>' for v in values)
    pages['publications.html'] = ('Publications',page_intro('Publications','Publications','Browse the publication library by year, research topic or title. Original titles and citation details are retained in English.',wide=True)+f'''
    <section class="container section-bottom"><div class="library-top"><p>{len(pubs)} publications · {min(years) if years else ''}–{max(years) if years else ''}</p><div>{link(c['scholar'],'Google Scholar ↗','text-link',True)}{link('assets/publications.bib','Download BibTeX ↓','text-link')}</div></div>
    <p class="small">{sum(p['entry_type']=='article' for p in pubs)} journal articles · {sum(p['entry_type']=='inproceedings' for p in pubs)} conference papers · {sum(p['entry_type'] not in {'article','inproceedings'} for p in pubs)} book chapter</p>
    <form class="publication-filters" role="search" id="publication-filters"><label class="search-label">Search publications<input id="pub-search" type="search" placeholder="Title, author, journal or keyword…" autocomplete="off"></label><label>Year<select id="pub-year"><option value="">All years</option>{options(years)}</select></label><label>Research topic<select id="pub-topic"><option value="">All topics</option>{options(topics)}</select></label><label>Type<select id="pub-type"><option value="">All types</option>{options(sorted({'Journal article' if p['entry_type']=='article' else 'Conference paper' if p['entry_type']=='inproceedings' else 'Book / chapter' for p in pubs}))}</select></label><button type="reset" class="reset-button">Reset</button></form>
    <p id="pub-count" class="small" role="status" aria-live="polite">Showing {len(pubs)} publications</p><div id="publication-list">{''.join(citation(p) for p in pubs)}</div><p id="pub-empty" class="empty-state" hidden>No publications match your filters. Try a different search.</p></section>''')

    member_sections = ''
    for role,plural in [('Senior Researcher','Senior Researchers'),('Researcher','Researchers'),('Research Assistant','Research Assistants')]:
        members = [p for p in people if p['role']==role]
        cards = ''.join(f'''<article class="member-card">{f'<img src="{safe_url(p["image"])}" alt="{h(p["name"])}" width="112" height="112" loading="lazy">' if p.get('image') else '<div class="member-initials" aria-hidden="true">'+h(''.join(s[0] for s in p['name'].split()[:2]))+'</div>'}<h3 class="notranslate" translate="no">{h(p['name'])}{orcid_link(p.get('orcid'),p['name'])}</h3><p>{h(p['bio'])}</p>{link(p['url'],'Profile ↗','text-link',True) if p.get('url') else ''}</article>''' for p in members)
        member_sections += f'<section class="people-section"><h2>{plural}</h2><div class="people-grid">{cards}</div></section>' if members else f'<section class="people-section"><h2>{plural}</h2><p class="empty-inline">Profiles will be added here.</p></section>'
    pages['people.html'] = ('People',page_intro('People','People','Meet the group lead, senior researchers, researchers and research assistants.')+f'''<section class="container section-bottom"><article class="lead-profile"><div class="lead-monogram notranslate" translate="no">HN</div><div><p class="eyebrow">Group lead</p><h2 class="notranslate" translate="no">Hoang Nguyen{orcid_link(c.get("orcid"),c["name"])}</h2><p class="lead-small">Principal Supervisor & Project Coordinator</p><p class="qualifications">{"<br>".join(h(item) for item in c["education"])}</p><div class="profile-links">{link('about.html','About Hoang ↗')}{link(c['scholar'],'Google Scholar ↗',external=True)}</div></div></article>{member_sections}</section>''')

    pages['news.html'] = ('News',page_intro('News','News','Published research, shared resources and updates from Hoang Nguyen Research Group.')+'<section class="container section-bottom"><div class="news-grid">'+''.join(news_card(n) for n in news)+'</div></section>')
    for n in news:
        pages['news/'+n['slug']+'.html'] = (n['title'],f'<article class="container article-page"><p class="eyebrow">{link("news.html","← All updates")}</p><div class="meta"><time datetime="{h(n["date"])}">{h(n["date"])}</time><span>{h(n["category"])}</span></div><h1>{h(n["title"])}</h1><div class="prose">{n["body"]}</div></article>')

    resources = [r for r in c['resources'] if r.get('published',True)]
    resource_cards = ''.join(f'<article class="resource-card"><p class="eyebrow">{h(r["type"])}</p><h2>{h(r["title"])}</h2><p>{h(r["description"])}</p>{link(r["url"],"Open resource ↗","text-link",True) if r.get("url") else '<span class="small">Materials forthcoming</span>'}</article>' for r in resources)
    if not resource_cards:
        resource_cards = '<div class="resource-empty"><span class="resource-glyph" aria-hidden="true">↗</span><h2>A place for shared learning.</h2><p>Teaching materials, practical exercises, code and other public resources will be added here.</p>'+link(c['github'],'Explore GitHub ↗','text-link',True)+'</div>'
    pages['resources.html'] = ('Teaching & Resources',page_intro('Teaching & Resources','Teaching & Resources','Course information and teaching materials.')+'<section class="container section-bottom"><div class="resources-grid">'+resource_cards+'</div></section>')

    join_cards = ''.join(f'<article class="join-card"><span class="row-number">{i+1}</span><h2>{h(j["title"])}</h2><p>{h(j["text"])}</p>{link("contact.html?topic="+quote(j["topic"]),"Start a conversation ↗","text-link")}</article>' for i,j in enumerate(c['join']))
    pages['join.html'] = ('Join Us',page_intro('Join us','Join Us','There are several ways to connect with the group. Introduce yourself and explain what you would like to work on.',wide=True)+f'<section class="container section-bottom"><div class="join-grid">{join_cards}</div><p class="availability-note">Enquiries are welcome. Opportunities, funding and supervision availability are discussed individually; no funded positions are advertised here.</p></section>')

    pages['contact.html'] = ('Contact',page_intro('Contact','Contact','Tell me a little about yourself, your interests and the question you have in mind.')+f'''
    <section class="container contact-grid section-bottom"><aside class="contact-details"><h2 class="notranslate" translate="no">Hoang Nguyen</h2><p>Group Lead · Principal Supervisor<br>Project Coordinator</p><dl><dt>Email</dt><dd>{link('mailto:'+c['email'],h(c['email']))}</dd><dt>Based in</dt><dd>{h(c['location'])}</dd><dt>Office</dt><dd class="muted">{h(c['office'])}</dd></dl><div class="profile-links">{link(c['scholar'],'Scholar ↗',external=True)}{link(c['orcid'],'ORCID ↗',external=True)}{link(c['github'],'GitHub ↗',external=True)}</div></aside>
    <form class="contact-form" action="{safe_url(c['form_endpoint'])}" method="POST" aria-label="Contact Hoang Nguyen"><input type="hidden" name="_subject" value="Research enquiry — nvthoang.com"><input type="hidden" name="_template" value="table"><input class="honeypot" type="text" name="_honey" tabindex="-1" autocomplete="off" aria-hidden="true" aria-label="Leave this field empty">
    <div class="form-row"><label>Your name <span aria-hidden="true">*</span><input name="name" required maxlength="150" autocomplete="name" placeholder="Full name"></label><label>Email <span aria-hidden="true">*</span><input type="email" name="email" required maxlength="254" autocomplete="email" placeholder="you@institution.org"></label></div>
    <label>Institution / organisation<input name="organisation" maxlength="200" autocomplete="organization" placeholder="Optional"></label>
    <label>I’m getting in touch about<select name="topic" id="contact-topic"><option>Research collaboration</option><option>Student research</option><option>Collaboration enquiry</option><option>Teaching / resources</option><option>Other enquiry</option></select></label>
    <label>Your message <span aria-hidden="true">*</span><textarea name="message" required minlength="15" maxlength="8000" rows="6" placeholder="Your interests, a research question, or a possible collaboration…"></textarea></label>
    <label class="consent"><input type="checkbox" name="consent" value="Contact details may be used to respond to this enquiry" required><span>I agree to my contact details being used to respond to this enquiry.</span></label>
    <p class="form-note">Messages are sent through FormSubmit, a third-party service. A spam check may appear after submission. {link('privacy.html','Privacy & translation')}</p><button type="submit" class="button">Send enquiry <span aria-hidden="true">↗</span></button><p class="form-status small" role="status" aria-live="polite"></p></form></section>''')

    pages['privacy.html'] = ('Privacy & Translation',page_intro('Website information','Privacy & translation.','How contact enquiries and the Vietnamese translation are handled.')+f'''<section class="container section-bottom"><div class="prose narrow"><h2>Contact enquiries</h2><p>The contact form sends the information you enter to FormSubmit so it can be forwarded to {h(c['email'])}. Your name, email, organisation, topic and message are used to respond to your enquiry. Do not include confidential research data or sensitive personal information.</p><p>The site itself does not maintain a contact database. FormSubmit may process and retain submissions under its own policies. {link('https://formsubmit.co/privacy.pdf','Read FormSubmit’s privacy policy',external=True)}. You may also contact Hoang directly by email.</p><h2>Vietnamese translation</h2><p>English is the original language of this website. The VI link opens the current public page in Google Translate’s Vietnamese view. Google processes the page content to provide the translation; its interface and availability are controlled by Google. Machine translations may contain errors, particularly in scientific terminology. Refer to the English original for precise wording.</p><p>The translated view uses a Google service address and may display a translation toolbar. This website does not store a Vietnamese copy or a translation cache. Some regions, browsers or pages may not support translation. {link('https://policies.google.com/privacy','Google privacy policy',external=True)}.</p><h2>Cookies and external links</h2><p>This website includes no analytics scripts, advertising trackers or external font requests. Visiting external links, translating a page, or submitting the form may invoke third-party services and their cookie policies.</p><h2>Questions</h2><p>{link('mailto:'+c['email'],h(c['email']))}</p></div></section>''')

    pages['404.html'] = ('Page not found',page_intro('404','This page could not be found.','The address may have changed. Return to the homepage or explore the research.')+'<section class="container section-bottom">'+link('index.html','Back to home ↗','button')+'</section>')
    for filename,(title,body) in pages.items():
        prefix = '../' if filename.startswith('news/') else ''
        page = render(c,title,body,filename,prefix=prefix,active='news.html' if prefix else '')
        if filename=='404.html':
            page = page.replace('<base href="./">','<base href="'+safe_url(c['site_url'].rstrip('/')+'/')+'">')
        (output/filename).write_text(page,encoding='utf-8')
    (output/'.nojekyll').write_text('',encoding='utf-8')
    (output/'CNAME').write_text(urlsplit(c['site_url']).hostname+'\n',encoding='utf-8')
    (output/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+c['site_url'].rstrip('/')+'/sitemap.xml\n',encoding='utf-8')
    urlset = ET.Element('urlset', xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')
    for name in pages:
        if name=='404.html': continue
        ET.SubElement(ET.SubElement(urlset,'url'),'loc').text=c['site_url'].rstrip('/')+'/'+('' if name=='index.html' else name)
    ET.ElementTree(urlset).write(output/'sitemap.xml',encoding='utf-8',xml_declaration=True)
    print(f'Built {len(pages)} pages, {len(pubs)} published records and {len(news)} news items → {output}')


if __name__=='__main__':
    try:
        build(ROOT/'dist')
    except (ValueError,KeyError,OSError,BibTeXError) as error:
        print('BUILD ERROR:',error,file=sys.stderr)
        sys.exit(1)
