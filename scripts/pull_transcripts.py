"""Run this locally, never in CI. Fills a PRIVATE vault with the full notes
(transcripts and article text) for every entry in the public vault, and can
pack that private vault into a zip to share.

Nothing is written inside this repo. Only notes the private vault is missing
get scraped, so a run after a monthly update costs about one Firecrawl credit
per new entry.

usage:
  python3 scripts/pull_transcripts.py --private /path/to/private-vault [--zip /path/to/out.zip] [--refresh]
  (or set YCKB_PRIVATE_VAULT instead of --private)
"""
import argparse, os, re, shutil, sys, tempfile, zipfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import yckb

ap = argparse.ArgumentParser()
ap.add_argument('--private', default=os.environ.get('YCKB_PRIVATE_VAULT'))
ap.add_argument('--repo', default=str(Path(__file__).resolve().parent.parent))
ap.add_argument('--zip', help='also write a shareable zip of the full vault here')
ap.add_argument('--refresh', action='store_true', help='re-scrape every transcript, not only missing ones')
args = ap.parse_args()
if not args.private: sys.exit('pass --private or set YCKB_PRIVATE_VAULT')
repo, private = Path(args.repo).resolve(), Path(args.private).expanduser().resolve()
public = repo / 'vault'
if private == public or repo in private.parents:
    sys.exit('the private vault must live outside this repo')
for d in ('Videos', 'Articles', 'People', 'Series', '_maps'): (private / d).mkdir(parents=True, exist_ok=True)

def has_full_text(p):
    t = p.read_text(errors='ignore')
    return '\n## Transcript' in t or '\n## Content' in t

# private notes by url; prefer a file without an iCloud " 2" suffix
priv = {}
for p in sorted(yckb.vault_notes(private), key=lambda p: (p.name.endswith(' 2.md'), not has_full_text(p))):
    priv.setdefault(yckb.note_url(p), p)

pulled = missing = 0
taken = yckb.taken_names(private)
for note in yckb.vault_notes(public):
    url = yckb.note_url(note)
    have = priv.get(url)
    if have and has_full_text(have) and not args.refresh: continue
    rec = yckb.parse_library_page(url, yckb.scrape(url))
    info = {}
    if rec['youtube_id'] and not rec['transcript']:
        info = yckb.parse_youtube(yckb.scrape(f'https://www.youtube.com/watch?v={rec["youtube_id"]}', max_age=0))
    section = yckb.full_text_section(rec, info)
    if not section:
        missing += 1; print(f'no transcript or text on YC or YouTube: {note.stem}'); continue
    target = have if have else private / note.parent.name / f'{yckb.free_name(note.stem, taken)}.md'
    text = note.read_text().rstrip()
    if section.startswith('\n## Transcript'):
        text = text.replace('\nhas_transcript: false\n', '\nhas_transcript: true\n', 1)
    target.write_text(text + '\n' + section)
    priv[url] = target; pulled += 1
    print(f'pulled: {note.stem}')

yckb.rebuild_indexes(private)
print(f'private vault: {pulled} notes pulled, {missing} without any text, firecrawl calls {yckb.CREDITS["used"]}')

if args.zip:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / 'YC Knowledge Base'
        for d in ('Videos', 'Articles', 'People', 'Series', '_maps', '.obsidian'): (out / d).mkdir(parents=True)
        for f in ('app.json', 'appearance.json', 'core-plugins.json', 'graph.json'):
            if (public / '.obsidian' / f).exists(): shutil.copy(public / '.obsidian' / f, out / '.obsidian' / f)
        shutil.copy(public / 'README.md', out / 'README.md')
        full = 0
        for note in yckb.vault_notes(public):
            src = priv.get(yckb.note_url(note))
            use = src if src and has_full_text(src) else note
            full += use is src
            shutil.copy(use, out / note.parent.name / note.name)
        yckb.rebuild_indexes(out)
        zpath = Path(args.zip).expanduser()
        with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            for p in sorted(out.rglob('*')):
                if p.is_file() and p.name != '.DS_Store':
                    z.write(p, p.relative_to(Path(tmp)))
        print(f'zip: {zpath} ({zpath.stat().st_size / 1e6:.1f} MB, {full} notes with full text)')
