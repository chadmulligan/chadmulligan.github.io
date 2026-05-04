#!/usr/bin/env python3
"""Regenerate the project cards in index.html from meta.json.

meta.json has the shape:

  {
    "projects": [
      {
        "title":       "...",       (required)
        "description": "...",       (required)
        "date":        "YYYY-MM",   (required)
        "url":         "...",       (optional — if present, the title links to it)
        "repo":        "owner/name" (optional — shown bottom-right, links to GitHub)
      },
      ...
    ]
  }

Cards are sorted by date descending; ties keep their order in the file.
"""
import html
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
META = ROOT / "meta.json"
START_MARKER = "<!-- PROJECTS_START -->"
END_MARKER = "<!-- PROJECTS_END -->"
INDENT = "          "  # 10 spaces — matches .proto-grid children


def fmt_date(date_str: str) -> str:
    """'2026-05' -> 'May 26'."""
    return datetime.strptime(date_str, "%Y-%m").strftime("%b %y")


def render_card(meta: dict) -> str:
    title = html.escape(meta["title"], quote=False)
    description = html.escape(meta["description"], quote=False)
    date_label = fmt_date(meta["date"])
    url = meta.get("url")
    repo = meta.get("repo")

    if url:
        title_html = (
            f'<a class="card-link" href="{html.escape(url)}" '
            f'target="_blank" rel="noopener">{title}</a>'
        )
    else:
        title_html = title

    repo_html = ""
    if repo:
        repo_url = f"https://github.com/{repo}"
        repo_html = (
            f'<a class="card-repo" href="{html.escape(repo_url)}" '
            f'target="_blank" rel="noopener">{html.escape(repo)}</a>'
        )

    lines = [
        '<div class="card">',
        '  <div class="card-top">',
        f'    <div class="card-title">{title_html}</div>',
        f'    <div class="card-description">{description}</div>',
        '  </div>',
        '  <div class="card-bottom">',
        f'    <div class="card-left"><span class="card-date">{date_label}</span></div>',
        f'    <div class="card-right">{repo_html}</div>',
        '  </div>',
        '</div>',
    ]
    return "\n".join(INDENT + line for line in lines)


def main() -> int:
    if not META.exists():
        print(f"meta.json not found at {META}", file=sys.stderr)
        return 1

    with META.open() as f:
        data = json.load(f)
    projects = data.get("projects", [])

    projects.sort(key=lambda p: p["date"], reverse=True)

    cards = [render_card(p) for p in projects]
    block = f"{START_MARKER}\n" + "\n".join(cards) + f"\n{INDENT}{END_MARKER}"

    text = INDEX.read_text()
    try:
        start = text.index(START_MARKER)
        end = text.index(END_MARKER) + len(END_MARKER)
    except ValueError:
        print(
            f"Markers {START_MARKER} / {END_MARKER} not found in {INDEX}",
            file=sys.stderr,
        )
        return 1

    new_text = text[:start] + block + text[end:]
    if new_text != text:
        INDEX.write_text(new_text)
        print(f"Updated {INDEX.relative_to(ROOT)} with {len(projects)} project card(s).")
    else:
        print(f"No changes ({len(projects)} project card(s)).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
