#!/usr/bin/env python3
"""
gen_pages.py - Generate .pages YAML files from front-matter metadata.
Works with mkdocs-gen-files plugin to auto-generate TOC without editing nav.

Reads YAML front-matter from .md files:
  ---
  title: Custom Title
  order: 1
  ---

Usage: Automatically runs during mkdocs build (via plugins.gen-files.scripts)
"""

import re
from pathlib import Path
from typing import Optional, Any
import yaml
import mkdocs_gen_files


def extract_frontmatter(file_path: Path) -> dict[str, Any]:
    """
    Extract YAML front-matter from a markdown file.
    Returns dict with title, order, etc. or empty dict if none found.
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        if not content.startswith("---"):
            return {}
        
        match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if not match:
            return {}
        
        frontmatter = yaml.safe_load(match.group(1)) or {}
        return frontmatter if isinstance(frontmatter, dict) else {}
    except Exception:
        return {}


def get_page_title(md_file: Path, frontmatter: dict) -> str:
    """Get page title from frontmatter or filename."""
    if "title" in frontmatter:
        return frontmatter["title"]
    # Fallback: filename to title case
    return md_file.stem.replace("_", " ").replace("-", " ").title()


def get_sort_key(order: Optional[int], filename: str) -> tuple:
    """
    Return sort key for ordering pages.
    Order from frontmatter takes precedence, then alphabetical by filename.
    """
    if order is not None:
        return (0, order, filename)  # Ordered items first
    return (1, filename)  # Then unordered items alphabetically


def generate_pages_file(folder_path: Path, docs_path: Path):
    """
    Generate .pages file for a folder based on .md files' front-matter.
    """
    md_files = sorted(
        [f for f in folder_path.glob("*.md") if f.name.lower() != "index.md"],
        key=lambda f: get_sort_key(
            extract_frontmatter(f).get("order"),
            f.name
        )
    )
    
    if not md_files:
        return
    
    pages_content = []
    
    for md_file in md_files:
        frontmatter = extract_frontmatter(md_file)
        title = get_page_title(md_file, frontmatter)
        
        # Format: "- Title: filename.md"
        pages_content.append(f"- {title}: {md_file.name}")
    
    if pages_content:
        rel_path = folder_path.relative_to(docs_path) / ".pages"
        pages_yaml = "\n".join(pages_content)
        
        with mkdocs_gen_files.open(str(rel_path), "w") as f:
            f.write(pages_yaml)


def main():
    """Scan docs folder and generate .pages for all subfolders."""
    # Assuming docs is at the root where mkdocs.yml is
    docs_path = Path(__file__).parent
    
    if not docs_path.exists():
        print(f"⚠ docs folder not found at {docs_path}")
        return
    
    print(f"🔄 Generating .pages files from front-matter...")
    
    # Scan all project folders (first-level subdirectories)
    for folder in sorted(docs_path.iterdir()):
        if folder.is_dir() and not folder.name.startswith(".") and folder.name != "site":
            generate_pages_file(folder, docs_path)
            print(f"  ✓ {folder.name}/.pages")
    
    print("✓ Done!")


if __name__ == "__main__":
    main()

