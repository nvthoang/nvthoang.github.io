#!/usr/bin/env python3
"""Check generated HTML, local links, anchors, image assets and metadata offline."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit, unquote
import json
import sys

ROOT = Path(__file__).resolve().parents[1]/'dist'


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path, self.links, self.ids, self.errors = path, [], set(), []
        self.base = path.as_uri()
        self.lang, self.title, self.h1 = False, False, 0
        self.feed(path.read_text(encoding='utf-8'))

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag=='html': self.lang = bool(a.get('lang'))
        if tag=='title': self.title = True
        if tag=='h1': self.h1 += 1
        if tag=='base': self.base = urljoin(self.base,a.get('href',''))
        if 'id' in a:
            if a['id'] in self.ids: self.errors.append('duplicate id '+a['id'])
            self.ids.add(a['id'])
        if tag=='img' and 'alt' not in a: self.errors.append('image has no alt attribute')
        if tag in {'a','script','img','link'} and not (tag=='script' and 'src' not in a):
            url = a.get('src' if tag in {'script','img'} else 'href','')
            if not url: self.errors.append('empty link/asset URL')
            self.links.append(url)


def main():
    pages = {p.resolve():Page(p.resolve()) for p in ROOT.rglob('*.html')}
    failures = []
    count = 0
    for path,page in pages.items():
        label = str(path.relative_to(ROOT))
        if not page.lang: page.errors.append('missing document language')
        if not page.title: page.errors.append('missing title')
        if page.h1 != 1: page.errors.append('expected one h1')
        if '{{' in path.read_text(encoding='utf-8'): page.errors.append('unresolved template field')
        for ref in page.links:
            parts = urlsplit(urljoin(page.base,ref))
            if parts.scheme != 'file': continue
            target = Path(unquote(parts.path)).resolve()
            if target.is_dir(): target /= 'index.html'
            count += 1
            if not target.is_file():
                page.errors.append('missing local target '+ref)
            elif parts.fragment and target.suffix=='.html' and target in pages and unquote(parts.fragment) not in pages[target].ids:
                page.errors.append('missing anchor '+ref)
        failures += [label+': '+err for err in page.errors]
    if not pages: failures.append('No generated HTML pages')
    if failures:
        print('\n'.join(failures),file=sys.stderr); return 1
    print(f'PASS: {len(pages)} pages; {count} local links/assets; language, headings, IDs and image alt attributes checked.')
    return 0


if __name__=='__main__':
    sys.exit(main())
