"""Macros for card navigation and weight validation (weight/sidebar_position)."""
from __future__ import annotations

import logging
from typing import Iterable, Tuple

from mkdocs.structure.nav import Section
from mkdocs.structure.pages import Page


# ---------------------------------------------------------------------------
# Card helpers
# ---------------------------------------------------------------------------

def _page_info(page: Page, config) -> Tuple[str, str, str] | None:
    """Return (title, url, description) for a page."""
    url = page.abs_url or page.url
    if url is None:
        return None
    if not getattr(page, "meta", None):
        page.read_source(config)
    desc = ""
    if isinstance(page.meta, dict):
        desc = page.meta.get("description", "") or ""
    return page.title, url, desc


def _link_for_section(section: Section, config) -> Tuple[str, str, str] | None:
    """Return (title, url, description) using the section's index if available."""
    target = next(
        (child for child in section.children if getattr(child, "is_page", False) and getattr(child, "is_index", False)),
        None,
    )
    if target is None:
        target = next((child for child in section.children if getattr(child, "is_page", False)), None)
    if target is None:
        return None
    info = _page_info(target, config)
    if info is None:
        return None
    title, url, desc = info
    return section.title or title, url, desc


def _item_info(item, config):
    """Return (title, url, description) for either a page or a section."""
    if getattr(item, "is_page", False):
        return _page_info(item, config)
    if getattr(item, "is_section", False):
        return _link_for_section(item, config)
    return None


def _section_for_page(nav, page) -> Section | None:
    """Return the nav section whose index page matches the current page."""
    def _walk(items):
        for item in items:
            if getattr(item, "is_section", False):
                idx = _index_page(item)
                if idx and idx.file == page.file:
                    return item
                found = _walk(item.children)
                if found:
                    return found
        return None

    return _walk(nav.items if nav else [])


def _count_children(section: Section) -> int:
    """Count direct child items (pages + subsections), including the index page."""
    return len(section.children)


def define_env(env):
    """MkDocs-macros entrypoint."""

    @env.macro
    def section_cards() -> str:
        """Render direct children of the current section as cards (page description or child count)."""
        nav = env.variables.get("nav")
        page = env.variables.get("page")
        config = env.variables.get("config")
        if not page:
            return ""

        parent = getattr(page, "parent", None)
        section = parent if getattr(parent, "is_section", False) else _section_for_page(nav, page) if nav else None
        if not section:
            return ""

        cards = []
        for child in section.children:
            if getattr(child, "is_page", False) and getattr(child, "is_index", False):
                continue
            if getattr(child, "is_page", False):
                info = _page_info(child, config)
                if not info:
                    continue
                title, url, desc = info
                icon = "&#128196;"  # page icon
                detail = desc
            elif getattr(child, "is_section", False):
                info = _link_for_section(child, config)
                if not info:
                    continue
                title, url, _ = info
                icon = "&#128193;"  # folder icon
                detail = f"{_count_children(child)} item(s)"
            else:
                continue

            cards.append(
                f"""
                <a class="section-card" href="{url}">
                  <div class="section-card__icon">{icon}</div>
                  <div class="section-card__body">
                    <div class="section-card__title">{title}</div>
                    <div class="section-card__desc">{detail or ""}</div>
                  </div>
                </a>
                """
            )

        if not cards:
            return ""

        style = """
<style id="section-cards-style">
.section-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1rem;
}
.section-card {
  display: flex;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  border-radius: 12px;
  text-decoration: none;
  background: var(--md-code-bg-color, #1f2937);
  border: 1px solid var(--md-default-fg-color--lighter, #2d3748);
  color: var(--md-default-fg-color, #e5e7eb);
  transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
}
.section-card:hover {
  border-color: var(--md-accent-fg-color, #5e81ac);
  box-shadow: 0 10px 25px rgba(0,0,0,0.18);
  transform: translateY(-2px);
}
.section-card__icon {
  font-size: 1.5rem;
  line-height: 1;
}
.section-card__body {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
.section-card__title {
  font-weight: 700;
  font-size: 0.875rem;
  color: var(--md-default-fg-color, #e5e7eb);
}
.section-card__desc {
  color: var(--md-default-fg-color--light, #cbd5e1);
  font-size: 0.6375rem;
}
</style>
"""
        return style + f'<div class="section-cards-grid">{"".join(cards)}</div>'


# ---------------------------------------------------------------------------
# Weight helpers and duplicate warnings (mkdocs-nav-weight compatibility)
# ---------------------------------------------------------------------------

def _index_page(section: Section) -> Page | None:
    """Return the index page for a section, if any."""
    return next(
        (child for child in section.children if getattr(child, "is_page", False) and getattr(child, "is_index", False)),
        None,
    )


def _get_weight(item, config) -> int | None:
    """Extract weight metadata for a page or section index."""
    page = item if getattr(item, "is_page", False) else _index_page(item) if getattr(item, "is_section", False) else None
    if page is None:
        return None
    page.read_source(config)
    meta = getattr(page, "meta", {}) or {}
    weight = meta.get("weight")
    return weight if isinstance(weight, (int, float)) else None


def _apply_sidebar_weight(item, config) -> None:
    """Populate weight from sidebar_position if weight is missing."""
    page = item if getattr(item, "is_page", False) else _index_page(item) if getattr(item, "is_section", False) else None
    if page is None:
        return

    page.read_source(config)
    meta = getattr(page, "meta", {}) or {}
    if "weight" not in meta and "sidebar_position" in meta:
        val = meta["sidebar_position"]
        if isinstance(val, (int, float, str)):
            text = str(val)
            if text.lstrip("-").replace(".", "", 1).isdigit():
                meta["weight"] = int(val) if text.isdigit() else float(text)
                page.meta = meta


def _warn_conflicts(items: list, parent_label: str, config) -> None:
    """Emit warnings for duplicate weights among sibling items."""
    weights: dict[int | float, list[str]] = {}
    for child in items:
        _apply_sidebar_weight(child, config)
        weight = _get_weight(child, config)
        if weight is None:
            continue
        title = getattr(child, "title", "Untitled")
        weights.setdefault(weight, []).append(title)

    for weight, titles in weights.items():
        if len(titles) > 1:
            logging.warning(
                "[nav-weight] Duplicate weight %s under '%s' for: %s",
                weight,
                parent_label or "root",
                ", ".join(titles),
            )


def _walk_sections(items: list, parent_label: str, config) -> None:
    """Traverse nav to find duplicate weights per sibling group."""
    _warn_conflicts(items, parent_label, config)
    for child in items:
        if getattr(child, "is_section", False):
            _walk_sections(child.children, child.title or parent_label, config)


def on_nav(nav, config, files):
    """Warn if siblings share the same weight."""
    _walk_sections(nav.items, "root", config)
    return nav
