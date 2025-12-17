# MkDocs Auto-TOC from Front-Matter

**Auto-generate Table of Contents (TOC) based on YAML front-matter metadata in `.md` files.**

## Overview
- ✅ No manual `nav:` editing in `mkdocs.yml`
- ✅ Control TOC order & titles via front-matter
- ✅ Dynamically generated at build time
- ✅ Python 3.12+ compatible (3.13.1 confirmed)
- ✅ Uses `mkdocs-gen-files` plugin (134⭐, 2.8k dependents)

## Prerequisites

```bash
pip install mkdocs mkdocs-material mkdocs-gen-files pyyaml
```

## How It Works

### 1. Add Front-Matter to `.md` Files
Each markdown file can have optional YAML front-matter:

```yaml
---
title: Custom Page Title
order: 1
---

# Heading

Your content here...
```

### 2. Automatic `.pages` Generation
The `gen_pages.py` script (runs automatically during build):
- Reads front-matter from all `.md` files in each folder
- Generates `.pages` YAML files with proper ordering
- Respects `order:` field for custom sort order
- Falls back to filename ordering if no `order` specified

### 3. Plugin Processes `.pages` Files
`mkdocs-gen-files` plugin:
- Executes `gen_pages.py` at build time
- `.pages` files are processed to build dynamic TOC
- TOC appears in sidebar navigation automatically

## Usage

### Example Folder Structure
```
docs/
  project_A/
    index.md              # order: 1
    guide.md              # order: 2
    advanced.md           # order: 3
  project_B/
    index.md
    tutorial.md
    faq.md
```

### Example Front-Matter

**`docs/project_A/index.md`:**
```yaml
---
title: Project A Overview
order: 1
---
# Project A
...
```

**`docs/project_A/guide.md`:**
```yaml
---
title: User Guide
order: 2
---
# User Guide
...
```

### Add a New Page

1. Create `.md` file in folder:
   ```bash
   echo "---
   title: My New Page
   order: 5
   ---
   
   # My New Page" > docs/project_A/newpage.md
   ```

2. Build/serve MkDocs:
   ```bash
   python -m mkdocs serve -f mkdocs.yml
   ```
   
3. TOC auto-updates! (`.pages` generated, sidebar refreshes)

### Change Order/Title

Simply edit the front-matter in your `.md` file:
```yaml
---
title: New Title
order: 10
---
```

Run build again → TOC updates automatically.

## Quick Start

```bash
# Install deps
pip install mkdocs mkdocs-material mkdocs-gen-files pyyaml

# Serve with live reload
python -m mkdocs serve -f mkdocs.yml

# Or build once
python -m mkdocs build -f mkdocs.yml
```

## Files

| File | Purpose |
|------|---------|
| `mkdocs.yml` | Config with `gen-files` plugin enabled |
| `gen_pages.py` | Script that reads front-matter & generates `.pages` files |
| `docs/**/.pages` | **AUTO-GENERATED** by `gen_pages.py` (don't edit) |

## Front-Matter Options

| Field | Type | Example | Required |
|-------|------|---------|----------|
| `title` | string | `"My Page Title"` | No (falls back to filename) |
| `order` | int | `1`, `2`, `3` | No (alphabetical if omitted) |

## Troubleshooting

### Build fails / `.pages` not generated
```bash
# Verify mkdocs-gen-files is installed
pip show mkdocs-gen-files

# Check gen_pages.py syntax
python gen_pages.py
```

### Changes not reflected in sidebar
- Ensure front-matter is valid YAML
- Check file is saved
- Clear browser cache (Ctrl+Shift+Del)
- Restart dev server

### Port 8000 already in use
```bash
python -m mkdocs serve -f mkdocs.yml -a 127.0.0.1:8001
```

## Example Project Structure

```
docs/
  mkdocs.yml             ← Main config (edit: theme, extensions, etc.)
  gen_pages.py           ← Generator script (auto-run at build)
  README.md              ← This file
  
  project_A/
    .pages               ← AUTO-GENERATED, DO NOT EDIT
    index.md             ← Must have front-matter
    license.md
    architecture.md
    
  project_B/
    .pages               ← AUTO-GENERATED
    index.md
    setup.md
    faq.md
```

## Notes

- ⚠️ **Do NOT manually edit `.pages` files** (auto-generated)
- ⚠️ **Do NOT manually edit `nav:` in `mkdocs.yml`** (will be ignored)
- ✅ Safe to edit: front-matter, `.md` content, theme config
- ✅ Add/remove files freely; TOC regenerates on each build
- 🔄 Live reload works: edit `.md` → server detects → TOC updates

---

**Built with**: `mkdocs-gen-files` (134⭐) + front-matter metadata

