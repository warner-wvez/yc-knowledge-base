# How it was built

The goal was simple to state and annoying to do: take the entire YC Startup Library and turn it into one connected, searchable knowledge base where every piece of advice is one click from its author, its series, and everything related to it.

This is the process, start to finish. None of it requires a server, a database, or a paid tool. The whole thing is plain Markdown files in folders.

---

## Step 1: Decide on one note per entry

The library is made of two kinds of things: videos (talks, podcasts, course sessions) and articles (essays and guides). Every single one becomes exactly one Markdown file. No file holds two entries. No entry is split across two files. One entry, one note. That single rule is what makes everything downstream possible.

There are 466 of these notes:

- 366 video notes
- 100 article notes

---

## Step 2: Pull the facts for each entry

For each entry, the same set of facts gets collected:

- Title
- Type (video or article)
- Author or speaker
- Series it belongs to
- Source URL on ycombinator.com
- For videos: the YouTube link, length, upload date, view count, and whether a transcript exists
- A short summary
- For videos: the original description

These are the facts that let you sort, filter, and link later. They are not an afterthought. They are the whole point.

---

## Step 3: Give every note structured frontmatter

Every note starts with a YAML frontmatter block. This is the part that turns a folder of text files into a queryable system. Here is the top of a real video note:

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

Because every note has the same fields in the same shape, you can ask the whole library questions like "show me every Lightcone episode" or "show me everything by this person" and get an answer instantly, with no code.

The full field list is in [Anatomy of a note](anatomy-of-a-note.md).

---

## Step 4: Link notes with wikilinks

A note is more useful when it is connected. Inside each note, the author and the series are written as `[[wikilinks]]`, not plain text:

```markdown
**Author:** [[Y Combinator]]
**Series:** [[Lightcone Podcast]]
**Source:** [YC Library](https://www.ycombinator.com/library/NN-agents-for-non-technical-users)
```

Those double brackets are live links. Click `[[Lightcone Podcast]]` and you land on the Lightcone series page. Click `[[Y Combinator]]` and you land on that author's page. This is what makes it a graph instead of a list. Every entry knows who made it and where it belongs.

---

## Step 5: Build the index maps

On top of the individual notes sit the index maps, in the `_maps/` folder and the vault home page. These are generated lists that give you a way in from the top:

- All Videos
- All Articles
- All Authors
- All Series

Plus two kinds of hub pages:

- **People pages** (one per author): every talk and essay that person has in the library, each linked.
- **Series pages** (one per series): every entry in that series, in order, each linked.

So you can navigate three ways: top down from a map, sideways from an author or a series, or by full-text search. You are never more than a click or two from anything.

---

## Step 6: Open it in Obsidian

The vault is built to be opened in [Obsidian](https://obsidian.md), a free app that reads plain Markdown and understands wikilinks. Obsidian gives you three things for free once the notes are structured this way:

1. **Full-text search** across every note at once.
2. **A graph view** that draws every author and series as a node and every link as an edge, so you can see the shape of the whole library.
3. **Backlinks**, so any author or series page automatically knows what points at it.

Nothing about the data is locked to Obsidian, though. It is all just Markdown. You could open it in any text editor, grep it from the terminal, or feed it to anything else. Obsidian is the nice front door, not the foundation.

---

## Why this design holds up

- **No lock-in.** Plain text files. They will open in 20 years.
- **No infrastructure.** No server, no database, nothing to maintain or pay for.
- **Self-describing.** The frontmatter means every note explains itself to a machine and a human at the same time.
- **Connected by default.** The wikilinks mean the value compounds as it grows. Every new note links into the existing graph instead of sitting in a pile.

The lesson, if there is one: a big collection of good information is not knowledge until it has structure. The structure here is boring on purpose. One note per entry, the same fields every time, links to author and series, maps on top. That is the entire trick.
