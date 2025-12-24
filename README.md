# MkDocs auto navigation (weight-based)

Navigation is generated directly from the `docs/` folder using `mkdocs-nav-weight` plus a tiny macros helper. Keep `nav:` empty in `mkdocs.yml`; ordering comes from page metadata.

## Prerequisites
```bash
pip install -r requirements.txt
# or
pip install mkdocs mkdocs-material mkdocs-nav-weight mkdocs-macros-plugin
```

## Navigation rules
- Use front matter `weight` to order siblings (lower = earlier). Items without a weight are alphabetical after weighted ones.
- `sidebar_position` is also accepted and normalized to `weight` by the macro shim.
- Duplicate weights among siblings emit warnings during the build; check the terminal output.
- Titles come from the first Markdown heading; descriptions can be set with a `description` field.

### Example front matter
```yaml
---
title: Overview
weight: 1
description: High-level entry point for the docs site.
---
```

## Developing locally
```bash
python -m mkdocs serve -f mkdocs.yml --dev-addr=localhost:8000
```

## Builds and checks
```bash
python -m mkdocs build -f mkdocs.yml        # production build
python -m mkdocs build -f mkdocs.yml --strict  # fail on warnings
```

### npm-style scripts (require Python + mkdocs installed)
```bash
npm run predev   # clean ./site
npm run dev      # live reload dev server
npm run build    # production build
npm run check    # strict build (warnings fail)
```

## Current layout
```
docs/
  AMB/
    index.md
  ECM/
    index.md
  Make Call/
    index.md
    design.md
    Make Call details/
      index.md
    Make call archiecture/
      index.md
```

## Notes
- `.pages` files are not used; ordering comes from `weight` (or `sidebar_position`) in front matter.
- Section landing cards are provided by the `section_cards` macro (see below).

## Section landing cards
- Add `{{ section_cards() }}` to any section index page to render direct children as cards.
- Pages show their title and `description` (from front matter); folders show their title and the number of immediate child items.
- Cards link to the child page/section and use the site color tokens for styling; no extra assets are required.
