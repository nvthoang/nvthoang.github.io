"""Small dependency-free reader for standard Google Scholar BibTeX exports.

Supports nested braces, quoted strings, string macros, # concatenation, and
crossref inheritance. Rejects malformed input instead of publishing partial data.
Not a TeX interpreter; content is always HTML-escaped by the site renderer.
"""
import re
import unicodedata


class BibTeXError(ValueError):
    pass


class Reader:
    def __init__(self, text):
        self.text, self.i = text, 0
        self.macros = dict(zip(
            "jan feb mar apr may jun jul aug sep oct nov dec".split(),
            "January February March April May June July August September October November December".split()))

    def error(self, message):
        line = self.text.count("\n", 0, self.i) + 1
        raise BibTeXError(f"BibTeX line {line}: {message}")

    def space(self):
        while self.i < len(self.text):
            if self.text[self.i].isspace():
                self.i += 1
            elif self.text[self.i] == "%":
                end = self.text.find("\n", self.i)
                self.i = len(self.text) if end == -1 else end + 1
            else:
                break

    def expect(self, char):
        self.space()
        if self.i >= len(self.text) or self.text[self.i] != char:
            self.error(f"expected {char!r}")
        self.i += 1

    def name(self):
        self.space()
        m = re.match(r"[\w:./+\-]+", self.text[self.i:])
        if not m:
            self.error("expected a field, key or entry type")
        self.i += len(m[0])
        return m[0]

    def delimited(self):
        opener = self.text[self.i]
        closer = '}' if opener == '{' else '"'
        self.i += 1
        start, depth = self.i, 0
        while self.i < len(self.text):
            char = self.text[self.i]
            if char == "\\":
                self.i += 2
                continue
            if opener == '"' and char == '"' and depth == 0:
                result = self.text[start:self.i]
                self.i += 1
                return result
            if char == '{':
                depth += 1
            elif char == '}':
                if depth == 0 and closer == '}':
                    result = self.text[start:self.i]
                    self.i += 1
                    return result
                depth -= 1
                if depth < 0:
                    self.error("unbalanced braces in quoted string")
            self.i += 1
        self.error("unclosed value")

    def value(self):
        parts = []
        while True:
            self.space()
            if self.i >= len(self.text):
                self.error("missing value")
            if self.text[self.i] in '{"':
                parts.append(self.delimited())
            else:
                token = self.name()
                if token.lower() not in self.macros and not token.isdigit():
                    self.error(f"undefined string macro {token!r}; wrap literal values in braces")
                parts.append(self.macros.get(token.lower(), token))
            self.space()
            if self.i >= len(self.text) or self.text[self.i] != '#':
                return ''.join(parts)
            self.i += 1

    def fields(self, close):
        fields = {}
        while True:
            self.space()
            if self.i >= len(self.text):
                self.error("unclosed entry")
            if self.text[self.i] == close:
                self.i += 1
                return fields
            name = self.name().lower()
            self.expect('=')
            fields[name] = self.value()
            self.space()
            if self.i < len(self.text) and self.text[self.i] == ',':
                self.i += 1
            elif self.i >= len(self.text) or self.text[self.i] != close:
                self.error("expected ',' between fields")

    def parse(self):
        entries, seen = [], set()
        while True:
            self.space()
            if self.i >= len(self.text):
                break
            self.expect('@')
            kind = self.name().lower()
            self.space()
            if self.i >= len(self.text) or self.text[self.i] not in '{(':
                self.error("expected '{' or '(' after entry type")
            close = '}' if self.text[self.i] == '{' else ')'
            self.i += 1
            if kind == 'comment':
                depth = 1
                open_char = '{' if close == '}' else '('
                while self.i < len(self.text) and depth:
                    c = self.text[self.i]
                    self.i += 1
                    if c == '\\':
                        self.i += 1
                        continue
                    depth += (c == open_char) - (c == close)
                if depth:
                    self.error("unclosed comment")
                continue
            if kind == 'preamble':
                self.value()
                self.expect(close)
                continue
            if kind == 'string':
                self.macros.update(self.fields(close))
                continue
            key = self.name()
            if key in seen:
                self.error(f"duplicate citation key {key!r}")
            seen.add(key)
            self.expect(',')
            entries.append(dict(self.fields(close), key=key, entry_type=kind))
        lookup = {e['key']: e for e in entries}
        def inherit(entry, stack):
            if entry['key'] in stack:
                raise BibTeXError('Circular crossref: ' + entry['key'])
            parent_key = entry.get('crossref')
            if not parent_key:
                return entry
            if parent_key not in lookup:
                raise BibTeXError('Missing crossref: ' + parent_key)
            return dict(inherit(lookup[parent_key], stack | {entry['key']}), **entry)
        return [inherit(e, set()) for e in entries]


def parse(text):
    return Reader(text).parse()


def plain(text):
    """Convert common BibTeX text commands to readable Unicode."""
    accents = {"'":'\u0301', '`':'\u0300', '^':'\u0302', '"':'\u0308', '~':'\u0303', '=':'\u0304', '.':'\u0307', 'v':'\u030c', 'c':'\u0327', 'u':'\u0306', 'H':'\u030b'}
    def accent(m):
        return unicodedata.normalize('NFC', m[2] + accents[m[1]])
    text = re.sub(r"\\(['`^\"~=\.vcuH])\s*\{?([A-Za-z])\}?", accent, text)
    for cmd, value in [('\\LaTeX','LaTeX'),('\\ss','ß'),('\\ae','æ'),('\\AE','Æ'),('\\oe','œ'),('\\o','ø'),('\\&','&'),('\\%','%'),('\\_','_'),('\\#','#'),('\\textendash','–')]:
        text = text.replace(cmd, value)
    text = re.sub(r"\\(?:textit|textbf|emph|textsc|mathrm|textrm)\s*", '', text)
    return re.sub(r'\s+', ' ', text.replace('{','').replace('}','').replace('~',' ').replace('---','—').replace('--','–')).strip()


def author_names(value):
    result = []
    # Split only outside braces, so corporate authors can contain "and".
    depth, start, i = 0, 0, 0
    names = []
    while i < len(value):
        if value[i] == '{': depth += 1
        if value[i] == '}': depth -= 1
        m = re.match(r'\s+and\s+', value[i:]) if depth == 0 else None
        if m:
            names.append(value[start:i])
            i += len(m[0]); start = i
        else: i += 1
    names.append(value[start:])
    for name in names:
        corporate = name.strip().startswith('{')
        parts = [plain(p) for p in name.split(',')]
        if len(parts) == 2 and not corporate:
            result.append(f'{parts[1]} {parts[0]}')
        elif len(parts) == 3 and not corporate:
            result.append(f'{parts[2]} {parts[0]}, {parts[1]}')
        else:
            result.append(plain(name))
    return ', '.join(result)


def publications(text):
    supported = {'article','inproceedings','incollection','inbook','book','proceedings'}
    records, doi_seen = [], set()
    for e in parse(text):
        if e['entry_type'] not in supported:
            continue
        if e.get('status', 'published').strip().lower() not in {'published','online first','early access'}:
            continue
        venue = plain(e.get('journal', e.get('booktitle', e.get('publisher',''))))
        if re.search(r'\b(arxiv|biorxiv|medrxiv|preprint|submitted|under review)\b', venue, re.I):
            continue
        if not e.get('title') or not re.fullmatch(r'\d{4}', e.get('year','')):
            raise BibTeXError(f"{e['key']}: a title and four-digit year are required")
        if not venue:
            raise BibTeXError(f"{e['key']}: add a journal, booktitle or publisher; review publication status")
        doi = re.sub(r'^https?://(?:dx\.)?doi\.org/', '', e.get('doi',''), flags=re.I).strip()
        if doi and not re.fullmatch(r'10\.\d{4,9}/\S+',doi,re.I):
            raise BibTeXError(f"{e['key']}: invalid DOI {doi!r}")
        if doi and doi.lower() in doi_seen:
            continue
        if doi: doi_seen.add(doi.lower())
        records.append(dict(e, title=plain(e['title']), authors=author_names(e.get('author','')), venue=venue,
                            year=int(e['year']), doi=doi, topics=[plain(t) for t in re.split('[,;]',e.get('keywords','')) if t.strip()]))
    return sorted(records, key=lambda p: (-p['year'],p['title'].casefold()))
