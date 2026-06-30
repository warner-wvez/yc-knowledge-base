# How it was built

The goal was simple to state and genuinely annoying to actually do. I wanted to take the entire YC Startup Library and turn it into one connected, searchable knowledge base, where every piece of advice sits one click away from its author, its series, and everything related to it.

What follows is the process from start to finish. None of it requires a server, a database, or a paid tool. The whole thing is simply plain Markdown files sitting in folders.

---

## Step 1: Decide on one note per entry

The library is made of two kinds of things: videos, which are the talks, podcasts, and course sessions, and articles, which are the essays and guides. Every single one of them becomes exactly one Markdown file. No file holds two entries, and no entry is ever split across two files. One entry, one note. That single rule is the thing that makes everything downstream possible.

There are 466 of these notes:

- 366 video notes
- 100 article notes

---

## Step 2: Pull the facts for each entry

For every entry, I pull the same set of facts:

- Title
- Type (video or article)
- Author or speaker
- Series it belongs to
- Source URL on ycombinator.com
- For videos: the YouTube link, length, upload date, view count, and whether a transcript exists
- A short summary
- For videos: the original description

These facts are not an afterthought. They are the whole point. The fact that every note carries the same fields in the same shape is exactly what lets you sort, filter, and link the library later.

---

## Step 3: Give every note structured frontmatter

Every note opens with a YAML frontmatter block, and this is the part that turns a plain folder of text files into something you can actually query. Here is the top of a real video note:

```yaml
---
title: Agents For Non-Technical Users
type: video
source: YC Library
url: "https://www.ycombinator.com/library/NN-agents-for-non-technical-users"
author: Y Combinator
series: Lightcone Podcast
youtube_id: 8SVocWnDHwE
youtube_url: "https://www.youtube.com/watch?v=8SVocWnDHwE"
upload_date: 2026-03-16
length: "39:32"
views: 47169
has_transcript: true
tags:
  - yc-library
  - video
  - series/lightcone-podcast
---
```

Because every note carries the same fields in the same shape, you can ask the whole library a question like "show me every Lightcone episode" or "show me everything by this person," and get an answer instantly, with no code at all.

The full field list is in [Anatomy of a note](anatomy-of-a-note.md).

---

## Step 4: Link notes with wikilinks

A note is far more useful when it is connected to the rest. So inside each note, the author and the series are written as `[[wikilinks]]`, not as plain text:

```markdown
**Author:** [[Y Combinator]]
**Series:** [[Lightcone Podcast]]
**Source:** [YC Library](https://www.ycombinator.com/library/NN-agents-for-non-technical-users)
```

Those double brackets are live links. Click `[[Lightcone Podcast]]` and you land on the Lightcone series page. Click `[[Y Combinator]]` and you land on that author's page. This is the single thing that makes it a graph instead of a list. Every entry knows who made it and where it belongs.

---

## Step 5: Build the index maps

On top of the individual notes sit the index maps, which live in the `_maps/` folder and on the vault home page. These are generated lists that give you a way in from the top:

- All Videos
- All Articles
- All Authors
- All Series

On top of that are two kinds of hub pages:

- **People pages** (one per author): every talk and essay that person has in the library, each one linked.
- **Series pages** (one per series): every entry in that series, in order, each one linked.

So there are three ways to navigate: top down from a map, sideways from an author or a series, or straight through full-text search. You are never more than a click or two away from anything.

---

## Step 6: Open it in Obsidian

The vault is built to be opened in [Obsidian](https://obsidian.md), a free app that reads plain Markdown and understands wikilinks. Once the notes are structured this way, Obsidian gives you three things for free:

1. **Full-text search** across every note at once.
2. **A graph view** that draws every author and series as a node and every link as an edge, so you can see the shape of the whole library at a glance.
3. **Backlinks**, so any author or series page automatically knows what points at it.

None of this is locked to Obsidian, though. It is all just Markdown. You could open it in any text editor, grep it from the terminal, or feed it to something else entirely. Obsidian is simply the nice front door, not the foundation.

---

## Why this design holds up

- **No lock-in.** These are plain text files, and they will still open in twenty years.
- **No infrastructure.** No server, no database, and nothing to maintain or pay for.
- **Self-describing.** The frontmatter means every note explains itself to a machine and a human at the same time.
- **Connected by default.** The wikilinks mean the value compounds as the library grows. Every new note links into the existing graph instead of just sitting in a pile.

Overall, the lesson I take from building this is simple: a big collection of good information is not knowledge until it has structure. And the structure here is boring on purpose. One note per entry, the same fields every time, links out to the author and the series, and maps sitting on top. That is the entire trick.
