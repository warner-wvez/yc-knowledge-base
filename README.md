# YC Knowledge Base

A personal second brain built from the entire [Y Combinator Startup Library](https://www.ycombinator.com/library). Every talk, podcast, and essay in the library was turned into one linked note, so that decades of startup advice becomes one searchable, connected graph instead of hundreds of videos and articles scattered across the internet.

This repo is the structure of that brain. It shows how it was built and what it gets used for. The full transcripts aren't included (see [A note on the content](#a-note-on-the-content)), but every note, link, author, and series is here, so you can see exactly how the system is wired together.

---

## At a glance

| | |
|---|---|
| Entries | **466** (366 videos, 100 articles) |
| Authors and speakers | **110** |
| Series and shows | **24** |
| Notes in the graph | **604** |
| Source | [Y Combinator Startup Library](https://www.ycombinator.com/library) |
| Tool | [Obsidian](https://obsidian.md) (plain Markdown, no lock-in) |

---

## Two ways to read this repo

**If you are a non-technical builder:** start with [How I use it](docs/how-i-use-it.md). It explains the actual point of all this. When you are building something and you hit a real decision, you do not want to vaguely remember that a YC partner once said something useful. You want to find it in ten seconds, read it, and see who said it and where. That is what this brain does. You do not need to know how it was built to get the idea.

**If you are a technical builder:** start with [How it was built](docs/how-it-was-built.md) and [Anatomy of a note](docs/anatomy-of-a-note.md). The interesting part is the data model: one Markdown file per entry, structured frontmatter for every field, wikilinks that connect each entry to its author and its series, and generated index maps that turn the whole thing into a navigable graph. No database, no app, just files.

Both paths lead to the same idea: a pile of great advice is not useful until it is structured. This is one way to structure it.

---

## What is inside

```
yc-knowledge-base/
├── README.md                 You are here.
├── docs/
│   ├── how-it-was-built.md    The build process, start to finish.
│   ├── how-i-use-it.md        What this brain is actually for.
│   └── anatomy-of-a-note.md   The schema behind every note.
└── vault/                    The brain itself. Open this folder in Obsidian.
    ├── README.md              The home map of the vault.
    ├── Videos/                366 talk and podcast notes.
    ├── Articles/              100 essay and guide notes.
    ├── People/                110 author pages, each listing their work.
    ├── Series/                24 series pages (Lightcone, Dalton & Michael, etc).
    └── _maps/                 Generated index maps across the whole library.
```

The `vault/` folder is a real Obsidian vault. Clone this repo, open that folder in Obsidian, and the graph comes alive: full-text search across everything, a visual graph of how every author and series connects, and one click from any talk to the person who gave it or the series it belongs to.

---

## How it was built, in one picture

```mermaid
flowchart TD
  A["YC Startup Library<br/>videos, podcasts, essays"] --> B["Pull each entry<br/>title, author, series, date, summary"]
  B --> C["Write one Markdown note per entry"]
  C --> D["Add structured frontmatter<br/>type, author, series, length, tags"]
  D --> E["Link every note to its author and series<br/>using wikilinks"]
  E --> F["Generate index maps<br/>All Videos, All Articles, All Authors, All Series"]
  F --> G["Open in Obsidian<br/>search the graph, follow the links"]
```

Full detail in [How it was built](docs/how-it-was-built.md).

---

## See it in action

The vault opens as a live graph in Obsidian. Below, the graph is colored by the six decision areas the brain gets used for. The grey nodes are the author and series pages: the connective spine. The colored nodes are the talks and essays that speak to a given decision, so when a real choice comes up, the relevant sources light up together.

<!-- Save your screenshot as docs/images/graph-view.png and it appears here automatically. -->
![Obsidian graph view of the knowledge base, colored by decision topic](docs/images/graph-view.png)

**Reading the colors:**

| Color | Decision area |
|---|---|
| Red | Getting into YC |
| Amber | Pricing and business model |
| Green | Fundraising and investors |
| Pink | Talking to users |
| Blue | Growth and distribution |
| Purple | Team, hiring, and cofounders |
| Grey | Author and series pages (the connective spine) |

---

## How the pieces connect

Every entry is linked to the person who made it and the series it belongs to. People pages list everything that person has in the library. Series pages list every entry in that series. Index maps sit on top and tie it all together. The result is a graph you can walk in any direction.

```mermaid
graph LR
  MAP["Index Maps"] --> SER["Series pages"]
  MAP --> PPL["People pages"]
  SER --> VID["Video notes"]
  SER --> ART["Article notes"]
  PPL --> VID
  PPL --> ART
  VID -. "same author or series" .-> ART
```

---

## A note on the content

All source material belongs to Y Combinator and the individual authors and speakers. It comes from the [Y Combinator Startup Library](https://www.ycombinator.com/library).

This repository contains the **structure** of the knowledge base: every note's title, its metadata, its short summary, the author and series links, and the index maps. It does **not** include the full video transcripts or the full text of the articles. Each note keeps a link back to its original source so credit and the real material always point home.

If you find this useful, go watch and read the originals at the [YC Startup Library](https://www.ycombinator.com/library). That is where the actual value lives. This repo is a map of it, not a copy of it.

---

## Explore it yourself

1. Clone the repo: `git clone <this repo>`
2. Install [Obsidian](https://obsidian.md) (free).
3. In Obsidian, choose "Open folder as vault" and pick the `vault/` folder.
4. Open the graph view and the home map (`vault/README.md`), then start clicking.

You can also just browse the Markdown files right here on GitHub. Start with [`vault/README.md`](vault/README.md).

---

## Why I built this

I'm a solo founder and business owner. The YC Startup Library is one of the best free collections of startup advice that exists out there, but it's spread across hundreds of hours of video and dozens of essays, and none of it is connected. When I'm making a real decision, I don't want to scrub through a two hour podcast hoping to re-find the thing I half-remember. I want to ask a question, get the handful of sources that actually speak to it, and see who said what and where.

So I built the brain that does that. This repo is how it works and what it is for.
