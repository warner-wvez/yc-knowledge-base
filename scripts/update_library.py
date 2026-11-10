"""Add every YC Startup Library entry the vault does not have yet.

Writes public notes only: metadata, summary, and YouTube description. Transcripts
and article text are never written here (check_public.py enforces that).

usage: python3 scripts/update_library.py [--repo .] [--max-new 300] [--dry-run] [--commit-msg-file PATH]
"""
import argparse, datetime, sys, textwrap
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import yckb

ap = argparse.ArgumentParser()
ap.add_argument('--repo', default='.')
ap.add_argument('--max-new', type=int, default=300, help='stop instead of scraping more than this many entries')
ap.add_argument('--dry-run', action='store_true', help='list new entries, scrape nothing')
ap.add_argument('--commit-msg-file')
args = ap.parse_args()

repo = Path(args.repo).resolve(); vault = repo / 'vault'
have = {yckb.entry_id(yckb.note_url(p)) for p in yckb.vault_notes(vault)}
live = yckb.live_entries()
new = {i: u for i, u in sorted(live.items()) if i not in have}
print(f'library lists {len(live)} entries, vault has {len(have)}, new: {len(new)}')
if not new: sys.exit(0)
if len(new) > args.max_new:
    sys.exit(f'{len(new)} new entries is more than --max-new {args.max_new}; check the sitemap before spending credits')
if args.dry_run:
    print('\n'.join(new.values())); sys.exit(0)

taken = yckb.taken_names(vault)
added, skipped, old_series = [], [], {p.stem for p in vault.glob('Series/*.md')}
old_people = {p.stem for p in vault.glob('People/*.md')}
for i, url in new.items():
    rec = yckb.parse_library_page(url, yckb.scrape(url))
    if yckb.is_placeholder(rec) or not rec['title']:
        skipped.append(url); continue
    info = yckb.parse_youtube(yckb.scrape(f'https://www.youtube.com/watch?v={rec["youtube_id"]}', max_age=0)) if rec['youtube_id'] else {}
    text, kind = yckb.public_note(rec, info)
    name = yckb.free_name(rec['title'], taken)
    (vault / ('Videos' if kind == 'video' else 'Articles') / f'{name}.md').write_text(text)
    added.append(dict(kind=kind, date=info.get('upload_date'), series=rec['carousel']))
    print(f'added {kind}: {name}')

yckb.rebuild_indexes(vault)
counts = yckb.update_counts(repo)
new_series = sorted({p.stem for p in vault.glob('Series/*.md')} - old_series)
new_people = len({p.stem for p in vault.glob('People/*.md')} - old_people)
print(f'added {len(added)}, skipped {len(skipped)} placeholder pages, firecrawl calls {yckb.CREDITS["used"]}, counts {counts}')

if args.commit_msg_file and added:
    today = datetime.date.today()
    cutoff = (today.replace(day=1) - datetime.timedelta(days=1)).replace(day=1).isoformat()  # first day of last month
    vids = [a for a in added if a['kind'] == 'video']
    recent = sum(1 for a in vids if a['date'] and a['date'] >= cutoff)
    n, nv, na = len(added), len(vids), len(added) - len(vids)
    plural = lambda k, word: f'{k} {word}' + ('' if k == 1 else 's')
    paras = [f'The vault now covers {counts["total"]} entries ({counts["videos"]} videos, {counts["articles"]} articles). '
             f'This run added {plural(nv, "video")} and {plural(na, "article")}. Notes carry the metadata, summary, '
             'and YouTube description only. Transcripts and article text stay out of the repo.']
    if vids:
        paras.append(f'{recent} of the new videos came out since {cutoff}. The other {nv - recent} are older videos '
                     'YC added to the library later.' if nv - recent else f'All {nv} new videos came out since {cutoff}.')
    if new_series or new_people:
        paras.append(f'New series: {", ".join(new_series) if new_series else "none"}. New author pages: {new_people}.')
    if skipped:
        paras.append(f'Skipped {plural(len(skipped), "placeholder page")} the library lists.')
    paras.append(f'Pulled with Firecrawl on {today.isoformat()} by the monthly workflow ({yckb.CREDITS["used"]} calls).')
    noun = 'entry' if n == 1 else 'entries'
    title = f'vault: Add {n} {noun} from the YC Startup Library for {today:%B %Y}'
    lines = [title, ''] + ['\n'.join(textwrap.wrap(p, 72)) + '\n' for p in paras]
    Path(args.commit_msg_file).write_text('\n'.join(lines).rstrip() + '\n')
