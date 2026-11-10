"""Fail if anything private is about to be published from this repo.

Checks every tracked or new file for transcript and article-text sections, API keys,
and absolute home-folder paths. The monthly workflow runs it before every push.
usage: python3 scripts/check_public.py [--repo .]
"""
import argparse, re, subprocess, sys
from pathlib import Path

ap = argparse.ArgumentParser(); ap.add_argument('--repo', default='.')
repo = Path(ap.parse_args().repo).resolve()
try:
    files = subprocess.run(['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'],
                           cwd=repo, capture_output=True, text=True, check=True).stdout.split('\0')
except (subprocess.CalledProcessError, FileNotFoundError):  # not a git checkout: check every file
    files = [str(p.relative_to(repo)) for p in repo.rglob('*') if p.is_file() and '.git' not in p.parts]
RULES = [
    ('transcript section', re.compile(r'^## Transcript\s*$', re.M), lambda f: f.startswith('vault/')),
    ('article full-text section', re.compile(r'^## Content\s*$', re.M), lambda f: f.startswith('vault/')),
    ('Firecrawl API key', re.compile(r'\bfc-[0-9a-f]{20,}'), lambda f: True),
    ('API key or token', re.compile(r'(?i)(api[_-]?key|secret|token)\s*[:=]\s*["\']?[A-Za-z0-9_\-]{20,}'), lambda f: True),
    ('home folder path', re.compile(r'/(Users|home)/[a-z][\w.-]+/'), lambda f: not f.startswith('vault/')),
]
bad = []
for f in filter(None, files):
    p = repo / f
    if not p.is_file() or p.stat().st_size > 5_000_000: continue
    try: text = p.read_text(errors='ignore')
    except Exception: continue
    for name, pat, applies in RULES:
        if applies(f) and pat.search(text): bad.append(f'{f}: {name}')
# Backstop: a public note is a few KB. One over 20 KB most likely carries a transcript.
# Untitled.md is the library sitemap, scraped by mistake in the first build (junk, not private).
KNOWN_LARGE = {'vault/Articles/Untitled.md'}
big = [f for f in filter(None, files) if re.match(r'vault/(Videos|Articles)/.+\.md$', f) and f not in KNOWN_LARGE
       and (repo / f).is_file() and (repo / f).stat().st_size > 20_000]
bad += [f'{f}: note over 20 KB, likely holds full text' for f in big]
if bad:
    print('Refusing to publish, private content found:'); print('\n'.join('  ' + b for b in bad)); sys.exit(1)
print(f'check_public: {len([f for f in files if f])} files clean')
