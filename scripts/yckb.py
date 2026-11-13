"""Shared code for keeping the vault in step with the YC Startup Library.

Standard library only, so it runs on a bare GitHub runner. Firecrawl is called
through its REST API with FIRECRAWL_API_KEY (or the Firecrawl CLI's stored key
when run locally).
"""
import html, json, os, re, time, unicodedata, urllib.request
from collections import defaultdict
from pathlib import Path

LIBRARY = 'https://www.ycombinator.com/library'
SITEMAP = LIBRARY + '/sitemap.xml'
ENTRY_RE = re.compile(r'/library/([A-Za-z0-9]{2})-[^/?#]*$')
# Library pages that are placeholders, not entries.
SKIP_SLUGS = {'2q-yc-startup-library', 'JH-coming-soon', 'KI-test'}
SKIP_TITLES = {'test', 'coming soon'}

# ---------------------------------------------------------------- firecrawl

def api_key():
    key = os.environ.get('FIRECRAWL_API_KEY')
    if key: return key
    cred = Path.home() / 'Library/Application Support/firecrawl-cli/credentials.json'
    if cred.exists(): return json.loads(cred.read_text())['apiKey']
    raise SystemExit('FIRECRAWL_API_KEY is not set')

CREDITS = {'used': 0}

def firecrawl(path, body, tries=3):
    req = urllib.request.Request(
        'https://api.firecrawl.dev/v2/' + path, data=json.dumps(body).encode(),
        headers={'Authorization': 'Bearer ' + api_key(), 'Content-Type': 'application/json'})
    for attempt in range(1, tries + 1):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                d = json.loads(r.read())
            if d.get('success'):
                CREDITS['used'] += 1
                return d
            err = d
        except Exception as e:  # network error, 429, 5xx
            err = e
        time.sleep(10 * attempt)
    raise RuntimeError(f'firecrawl {path} failed for {body.get("url")}: {err}')

def scrape(url, max_age=None):
    body = {'url': url, 'formats': ['markdown']}
    if max_age is not None: body['maxAge'] = max_age
    return firecrawl('scrape', body)['data']

# When YouTube's transcript panel fails to load, the scrape returns the page's list of suggested
# videos under a "Transcript" heading. Two private notes got that junk instead of a transcript.
PAGE_JUNK = re.compile(r'i\.ytimg\.com/|hqdefault\.jpg|NaN / NaN|\]\(https://www\.youtube\.com/watch\?v=')

def looks_like_transcript(t):
    """True for spoken text; False for empty text or a scraped list of thumbnails and video links."""
    if not t or len(t.strip()) < 200 or PAGE_JUNK.search(t): return False
    lines = [l for l in t.splitlines() if l.strip()]
    return sum(l.lstrip().startswith(('[', '![', '###')) for l in lines) <= len(lines) * 0.2

def library_page_transcript(url):
    """The transcript YC embeds in the library page's own data. A plain GET, no Firecrawl credit."""
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (yc-knowledge-base)'})
    try:
        raw = urllib.request.urlopen(req, timeout=60).read().decode('utf-8', 'replace')
    except Exception:
        return None
    m = re.search(r'&quot;transcript&quot;:&quot;(.*?)&quot;,&quot;', raw, re.S)
    if not m: return None
    try:
        t = json.loads(html.unescape('"' + m.group(1) + '"')).strip()
    except ValueError:
        return None
    return t if looks_like_transcript(t) else None

# ---------------------------------------------------------------- discovery

def live_entries():
    """{2-char id: url} for every entry YC lists: the library sitemap plus a Firecrawl map
    (the map has caught a few entries the sitemap leaves out)."""
    req = urllib.request.Request(SITEMAP, headers={'User-Agent': 'Mozilla/5.0 (yc-knowledge-base updater)'})
    xml = urllib.request.urlopen(req, timeout=60).read().decode()
    urls = [u.replace('&amp;', '&') for u in re.findall(r'<loc>([^<]+)</loc>', xml)]
    try:
        links = firecrawl('map', {'url': LIBRARY, 'limit': 5000})['links']
        urls += [l['url'] if isinstance(l, dict) else l for l in links]
    except RuntimeError as e:
        print('map failed, using the sitemap alone:', e)
    out = {}
    for u in urls:
        u = u.split('?')[0].split('#')[0].rstrip('/')
        m = ENTRY_RE.search(u)
        if m and u.split('/library/')[1] not in SKIP_SLUGS:
            out.setdefault(m.group(1), u)
    return out

def note_url(path):
    m = re.search(r'^url: "?([^"\n]+)', Path(path).read_text(errors='ignore'), re.M)
    return m.group(1) if m else None

def entry_id(url):
    m = ENTRY_RE.search(url or '')
    return m.group(1) if m else None

def vault_notes(vault):
    return sorted(list(Path(vault).glob('Videos/*.md')) + list(Path(vault).glob('Articles/*.md')))

# ---------------------------------------------------------------- parsing

def clean_names(s):
    """'[A](url), [B](url), and [C](url)' -> 'A, B, C'"""
    s = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', s).strip()
    s = re.sub(r',?\s+and\s+', ', ', s)
    s = re.sub(r'\s*,\s*', ', ', s)
    return s.strip(' ,') or None

def parse_library_page(url, data):
    md, meta = data.get('markdown', '') or '', data.get('metadata', {}) or {}
    i = md.find('[Home](https://www.ycombinator.com/library)')
    body = md[i:] if i >= 0 else md
    end = body.find('\n## Footer')
    body = body[:end] if end >= 0 else body
    car = re.match(r'\[Home\]\([^)]+\)›\s*\n+\[([^\]]+)\]\(https://www\.ycombinator\.com/library/carousel/[^)]+\)›', body)
    h1 = re.search(r'^# (.+)$', body, re.M)
    title = h1.group(1).strip() if h1 else (meta.get('ogTitle') or '').split('  :')[0].strip()
    after = body[h1.end():] if h1 else body
    by = re.match(r'\s*\n+by ?([^\n]*)\n', after)
    yt = re.search(r'\[Watch on\]\(https://www\.youtube\.com/watch\?v=([A-Za-z0-9_-]{11})', body) \
        or re.search(r'img\.youtube\.com/vi/([A-Za-z0-9_-]{11})/', str(meta.get('ogImage') or ''))
    tx = None
    m = re.search(r'\n## Transcript\s*\n(.*)', body, re.S)
    if m:
        cut = re.search(r'\n1\. (Up next|Related)', m.group(1))
        tx = (m.group(1)[:cut.start()] if cut else m.group(1)).strip() or None
    yc_desc = None
    if m:
        keep = []
        for p in reversed([p.strip() for p in re.split(r'\n\s*\n', body[:m.start()]) if p.strip()]):
            if re.match(r'^(— |\d{1,2}:\d{2}|## |\[|!\[)', p) or re.search(r'\d+ (months?|years?|weeks?|days?) ago$', p): break
            keep.insert(0, p)
        yc_desc = '\n\n'.join(keep) or None
    content = None
    if not yt and by:
        c = after[by.end():]
        cut = re.search(r'\n1\. (Up next|Related)|\n## Related', c)
        c = c[:cut.start()] if cut else c
        c = re.sub(r'!\[YC Logo\]\([^)]*\)\s*\n+# What is Y Combinator\?.*?\[Apply\]\(https://www\.ycombinator\.com/apply\)\s*\n', '\n', c, flags=re.S)
        content = c.strip() or None
    return dict(url=url, title=title, author=clean_names(by.group(1)) if by and by.group(1).strip() else None,
                carousel=car.group(1).strip() if car else None, youtube_id=yt.group(1) if yt else None,
                meta_description=str(meta.get('description') or '').strip(), yc_description=yc_desc,
                transcript=tx, content=content)

def parse_youtube(data):
    md = data.get('markdown', '') or ''
    g = lambda pat: (re.search(pat, md).group(1).strip() if re.search(pat, md) else None)
    desc = re.search(r'##\s*Description\s*\n+```\n(.*?)\n```', md, re.S)
    tx = re.search(r'\n##\s*Transcript\s*\n+(.+?)(?:\n##\s|\Z)', md, re.S)
    views = g(r'\*\*Views\*\*:\s*([0-9,]+)')
    return dict(upload_date=g(r'\*\*Uploaded at\*\*:\s*([0-9-]+)'), length=g(r'\*\*Length\*\*:\s*([0-9:]+)'),
                views=int(views.replace(',', '')) if views else None,
                yt_description=desc.group(1).strip() if desc else None,
                transcript=tx.group(1).strip() if tx and looks_like_transcript(tx.group(1)) else None)

def is_placeholder(rec):
    return (rec['title'] or '').strip().lower() in SKIP_TITLES

# ---------------------------------------------------------------- notes

def safe_filename(s):
    if not s: return 'untitled'
    s = re.sub(r'[\\/:*?"<>|]+', '-', s)
    s = re.sub(r'\s+', ' ', s).strip().strip('.')
    return s[:120] or 'untitled'

def link(target, alias):
    return f'[[{target}]]' if target == alias else f'[[{target}|{alias}]]'

def yaml_scalar(v):
    if isinstance(v, bool): return 'true' if v else 'false'
    s = str(v)
    if any(c in s for c in ':#\n"\'[]{}&*!|>%@`') or s.startswith('-') or s.strip() != s or s == '':
        return '"' + s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ') + '"'
    return s

def yaml_block(d):
    out = ['---']
    for k, v in d.items():
        if v is None or v == '' or v == []: continue
        if isinstance(v, list): out += [f'{k}:'] + [f'  - {yaml_scalar(i)}' for i in v]
        else: out.append(f'{k}: {yaml_scalar(v)}')
    return '\n'.join(out + ['---'])

def public_note(rec, info):
    """The note as the public repo stores it: metadata, summary, YouTube description. No transcript."""
    title, author, carousel, yt, url = rec['title'], rec['author'], rec['carousel'], rec['youtube_id'], rec['url']
    kind = 'video' if yt else 'article'
    yt_desc = (info.get('yt_description') or '').strip()
    meta = rec['meta_description']
    bare = re.sub(rf'^{re.escape(carousel)}:\s*', '', meta) if carousel else meta
    summary = meta if bare else ((rec['yc_description'] or '').split('\n\n')[0]
                                 or (rec['content'] or '').split('\n\n')[0] or yt_desc.split('\n\n')[0])
    fm = {'title': title, 'type': kind, 'source': 'YC Library', 'url': url, 'author': author, 'series': carousel}
    if yt:
        fm.update(youtube_id=yt, youtube_url=f'https://www.youtube.com/watch?v={yt}',
                  upload_date=info.get('upload_date'), length=info.get('length'), views=info.get('views'))
    fm['has_transcript'] = bool(rec['transcript'] or info.get('transcript'))
    fm['tags'] = ['yc-library', kind] + (['series/' + re.sub(r'[^a-z0-9]+', '-', carousel.lower()).strip('-')] if carousel else [])
    ml = []
    if author: ml.append(f'**Author:** {link(safe_filename(author), author)}')
    if carousel: ml.append(f'**Series:** {link(safe_filename(carousel), carousel)}')
    if yt:
        ml.append(f'**Video:** [Watch on YouTube]({fm["youtube_url"]})')
        if info.get('length'): ml.append(f'**Length:** {info["length"]}')
        if info.get('upload_date'): ml.append(f'**Uploaded:** {info["upload_date"]}')
    ml.append(f'**Source:** [YC Library]({url})')
    parts = [yaml_block(fm), '', f'# {title}', '', '  \n'.join(ml), '']
    if summary: parts += ['## Summary', '', summary.strip(), '']
    if yt_desc and yt_desc != summary: parts += ['## YouTube Description', '', yt_desc, '']
    return '\n'.join(parts).rstrip() + '\n', kind

def full_text_section(rec, info):
    """The part the public repo leaves out: the transcript, or an article's full text."""
    tx = rec['transcript'] or (info or {}).get('transcript')
    if tx: return '\n## Transcript\n\n' + tx + '\n'
    if rec['content']: return '\n## Content\n\n' + rec['content'] + '\n'
    return ''

def taken_names(vault):
    """Filenames already used, folded the way macOS compares them (case and accents)."""
    return {unicodedata.normalize('NFC', p.stem).casefold() for p in Path(vault).glob('*/*.md')}

def free_name(title, taken):
    base = safe_filename(title); name, n = base, 1
    while unicodedata.normalize('NFC', name).casefold() in taken:
        n += 1; name = f'{base} ({n})'
    taken.add(unicodedata.normalize('NFC', name).casefold())
    return name

# ---------------------------------------------------------------- indexes

def fm_value(fm, key):
    m = re.search(rf'^{key}: (.*)$', fm, re.M)
    if not m: return None
    v = m.group(1).strip()
    return v[1:-1].replace('\\"', '"').replace('\\\\', '\\') if v.startswith('"') and v.endswith('"') else v

def rebuild_indexes(vault):
    """Rewrite People/, Series/ and _maps/ from the notes' frontmatter (same layout as the first build)."""
    root = Path(vault)
    notes = [(p.parent.name, p, p.read_text().split('\n---\n', 1)[0]) for p in vault_notes(root)]
    by_url = defaultdict(list)
    for folder, p, fm in notes: by_url[fm_value(fm, 'url')].append((p, fm))
    def stray_copy(p, fm):  # same url, filename not derived from the title: leave it out
        group = by_url[fm_value(fm, 'url')]
        canon = [q for q, f in group if unicodedata.normalize('NFC', q.stem) == unicodedata.normalize('NFC', safe_filename(fm_value(f, 'title')))]
        return len(group) > 1 and bool(canon) and p not in canon
    written, authors, series = [], defaultdict(list), defaultdict(list)
    for folder, p, fm in notes:
        if stray_copy(p, fm): continue
        title, kind = fm_value(fm, 'title'), fm_value(fm, 'type')
        rel = unicodedata.normalize('NFC', f'{folder}/{p.name}')
        written.append(dict(path=rel, title=title, kind=kind, tx=fm_value(fm, 'has_transcript') == 'true'))
        if fm_value(fm, 'author'): authors[fm_value(fm, 'author')].append((title, rel, kind))
        if fm_value(fm, 'series'): series[fm_value(fm, 'series')].append((title, rel, kind))
    head = lambda t, k: f'---\ntitle: {yaml_scalar(t)}\ntype: {k}\ntags:\n  - yc-library\n  - {k}\n---\n\n'
    item = lambda title, rel, kind: f'- {link(Path(rel).stem, title)} _({kind})_\n'
    for a, items in authors.items():
        (root / 'People' / (safe_filename(a) + '.md')).write_text(
            head(a, 'person') + f'# {a}\n\nYC Library entries: **{len(items)}**\n\n## Talks and Essays\n\n'
            + ''.join(item(*i) for i in sorted(items)))
    for s, items in series.items():
        (root / 'Series' / (safe_filename(s) + '.md')).write_text(
            head(s, 'series') + f'# {s}\n\nEntries in this series: **{len(items)}**\n\n' + ''.join(item(*i) for i in sorted(items)))
    maps = root / '_maps'
    group = lambda idx: '\n'.join(f'## {link(safe_filename(k), k)}\n\n' + ''.join(item(*i) for i in sorted(idx[k])) for k in sorted(idx))
    (maps / 'All Series.md').write_text(head('All Series', 'moc') + '# All Series\n\n' + group(series).rstrip() + '\n')
    (maps / 'All Authors.md').write_text(head('All Authors', 'moc') + '# All Authors\n\n' + group(authors).rstrip() + '\n')
    vids = sorted((w for w in written if w['kind'] == 'video'), key=lambda w: w['title'].lower())
    arts = sorted((w for w in written if w['kind'] == 'article'), key=lambda w: w['title'].lower())
    (maps / 'All Videos.md').write_text(head('All Videos', 'moc') + '# All Videos\n\n' + ''.join(
        f'- {link(Path(w["path"]).stem, w["title"])}{" 📝" if w["tx"] else ""}\n' for w in vids))
    (maps / 'All Articles.md').write_text(head('All Articles', 'moc') + '# All Articles\n\n' + ''.join(
        f'- {link(Path(w["path"]).stem, w["title"])}\n' for w in arts))
    return {s: len(i) for s, i in series.items()}

# ---------------------------------------------------------------- counts in the docs

def update_counts(repo):
    """Refresh every count the README, docs and vault home map quote."""
    repo = Path(repo); v = repo / 'vault'
    videos, articles = len(list(v.glob('Videos/*.md'))), len(list(v.glob('Articles/*.md')))
    with_tx = sum('\nhas_transcript: true\n' in p.read_text() for p in v.glob('Videos/*.md'))
    people, series_n = len(list(v.glob('People/*.md'))), len(list(v.glob('Series/*.md')))
    total = videos + articles
    graph = total + people + series_n + len(list(v.glob('_maps/*.md')))
    edits = {
        'README.md': [
            (r'(\| Entries \| \*\*)\d+(\*\* \()\d+( videos, )\d+( articles\) \|)', rf'\g<1>{total}\g<2>{videos}\g<3>{articles}\g<4>'),
            (r'(\| Authors and speakers \| \*\*)\d+', rf'\g<1>{people}'),
            (r'(\| Series and shows \| \*\*)\d+', rf'\g<1>{series_n}'),
            (r'(\| Notes in the graph \| \*\*)\d+', rf'\g<1>{graph}'),
            (r'(Videos/\s+)\d+( talk and podcast notes)', rf'\g<1>{videos}\g<2>'),
            (r'(Articles/\s+)\d+( essay and guide notes)', rf'\g<1>{articles}\g<2>'),
            (r'(People/\s+)\d+( author pages)', rf'\g<1>{people}\g<2>'),
            (r'(Series/\s+)\d+( series pages)', rf'\g<1>{series_n}\g<2>')],
        'docs/how-it-was-built.md': [
            (r'(There are )\d+( of these notes:)', rf'\g<1>{total}\g<2>'),
            (r'(\n- )\d+( video notes)', rf'\g<1>{videos}\g<2>'),
            (r'(\n- )\d+( article notes)', rf'\g<1>{articles}\g<2>')],
        'docs/how-i-use-it.md': [(r'(A folder of )\d+( unconnected)', rf'\g<1>{total}\g<2>')],
        'vault/README.md': [
            (r'(\*\*)\d+( entries\*\*)', rf'\g<1>{total}\g<2>'),
            (r'(\*\*)\d+( videos\*\* \()\d+( with)', rf'\g<1>{videos}\g<2>{with_tx}\g<3>'),
            (r'(\*\*)\d+( articles\*\*)', rf'\g<1>{articles}\g<2>'),
            (r'(\*\*)\d+( authors and speakers\*\*)', rf'\g<1>{people}\g<2>'),
            (r'(\*\*)\d+( series and shows\*\*)', rf'\g<1>{series_n}\g<2>'),
            (r'(the full list of )\d+', rf'\g<1>{people}')],
    }
    for name, subs in edits.items():
        p = repo / name
        if not p.exists(): continue
        s = p.read_text()
        for pat, rep in subs:
            s, n = re.subn(pat, rep, s, count=1)
            if n != 1: print(f'warning: count pattern not found in {name}: {pat}')
        p.write_text(s)
    # series list on the vault home map
    home = v / 'README.md'
    if home.exists():
        rows = {}
        for f in v.glob('Series/*.md'):
            t = f.read_text()
            rows[re.search(r'^# (.+)$', t, re.M).group(1)] = (f.stem, re.search(r'Entries in this series: \*\*(\d+)', t).group(1))
        block = ''.join(f'- {link(unicodedata.normalize("NFC", rows[k][0]), k)} ({rows[k][1]})\n' for k in sorted(rows))
        home.write_text(re.sub(r'(## Series\n\n)(?:- \[\[.*\n)+', lambda m: m.group(1) + block, home.read_text()))
    return dict(total=total, videos=videos, articles=articles, with_tx=with_tx, people=people, series=series_n)
