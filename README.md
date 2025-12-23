# MkDocs Auto Navigation (weight-based, no manual nav edits)

Navigation is built directly from the `docs/` folder; ordering is controlled with a `weight` field in each page's front matter via `mkdocs-nav-weight`.

## Prerequisites

```bash
pip install mkdocs mkdocs-material mkdocs-nav-weight
```

## How it works
- Leave `nav:` empty in `mkdocs.yml`; MkDocs builds the nav from the folder tree.
- Ordering is controlled per page by a `weight` field in the YAML front matter; lower numbers appear first. Pages without `weight` are ordered alphabetically after weighted items.
- Page titles come from the first Markdown heading (fallback: filename).

### Example front matter
```yaml
---
title: Overview
weight: 1
---
```

## Usage
1) Add or edit Markdown files anywhere under `docs/`.
2) Serve or build:
   ```bash
   python -m mkdocs serve -f mkdocs.yml
   # or
   python -m mkdocs build -f mkdocs.yml
   ```
3) The sidebar updates automatically based on the current folder structure and `weight` values.

### npm-style shortcuts
`package.json` includes scripts so you can use familiar npm commands (requires Python + mkdocs installed):
```bash
npm run docs:serve   # live reload
npm run docs:build   # production build
npm run docs:check   # strict build (fails on warnings)
```

## Project layout (example)
```
docs/
  mkdocs.yml
  README.md
  index.md
  about.md
  ECM/
    index.md
  Make Call/
    index.md
    Make Call details/
      index.md
```

## Notes
- No helper script is needed; `gen_pages.py` has been removed.
- `.pages` files are not used; ordering comes from `weight` in front matter.
- Keep `nav:` empty in `mkdocs.yml`; MkDocs + `mkdocs-nav-weight` manage navigation.
