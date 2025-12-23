"""Macros for rendering section link cards in MkDocs pages."""
from __future__ import annotations

from typing import Iterable, Tuple

from mkdocs.structure.nav import Section
from mkdocs.structure.pages import Page


def _page_info(page: Page, config) -> Tuple[str, str, str] | None:
    """Return (title, url, description) for a page."""
    if page.url is None and page.abs_url is None:
        return None
    # Ensure meta is populated
    if not getattr(page, "meta", None):
        page.read_source(config)
    desc = ""
    if isinstance(page.meta, dict):
        desc = page.meta.get("description", "") or ""
    url = page.abs_url or page.url
    return page.title, url, desc


def _link_for_section(section: Section, config) -> Tuple[str, str, str] | None:
    """Return (title, url, description) for a section using its index page if available."""
    # Prefer an index page; fallback to first page child.
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


def _section_items(section: Section, config) -> Iterable[Tuple[str, str, str]]:
    """Yield (title, url, description) for direct children of a section."""
    for child in section.children:
        if getattr(child, "is_page", False):
            if getattr(child, "is_index", False):
                continue
            info = _page_info(child, config)
            if info:
                yield info
        elif getattr(child, "is_section", False):
            link = _link_for_section(child, config)
            if link:
                yield link


def define_env(env):
    """MkDocs-macros entrypoint."""

    @env.macro
    def section_cards(include_index: bool = False) -> str:
        """
        Render cards for the current section's immediate children.

        - include_index: whether to include the section index page itself (default: False)
        """
        page: Page | None = env.variables.get("page")
        if page is None:
            return ""

        # Use parent section for index pages; otherwise use the page's section.
        section = page.parent if page.is_page else None
        if section is None:
            return ""

        config = env.variables.get("config")
        items = list(_section_items(section, config))
        if include_index and page.url:
            desc = ""
            if isinstance(getattr(page, "meta", None), dict):
                desc = page.meta.get("description", "") or ""
            items = [(page.title, page.url, desc)] + items

        if not items:
            return ""

        # Render as Material grid cards using plain HTML.
        lines = ['<div class="grid cards">']
        for title, url, desc in items:
            lines.append(
                f'  <a class="card" href="{url}">'
                f'<span class="md-ellipsis">{title}</span>'
                f'<p class="md-typeset__text" style="color:#555;font-size:0.85em;margin:0;">'
                f'{desc} <span aria-hidden="true">→</span></p>'
                f"</a>"
            )
        lines.append("</div>")

        return "\n".join(lines)
