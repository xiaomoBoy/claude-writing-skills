#!/usr/bin/env python3
"""
Normalize markdown image paths so wechatsync (and other publish CLIs) can
actually read them.

What it does:
1. URL-decode image paths (Obsidian writes spaces as %20, also encodes CJK)
2. Resolve to the real file: first relative to the markdown file, then relative
   to a root directory (auto-detected git repo root, or MD_VAULT_ROOT env)
3. Rewrite the link as a path relative to the markdown file

Defaults to in-place modification. Use --dry-run to preview.

Why this exists: wechatsync does not URL-decode image src, so percent-encoded
paths (which Obsidian writes by default) silently break image upload.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import urllib.parse
from pathlib import Path


# ![alt](path)  — alt allows everything except ], path allows everything except )
IMG_PATTERN = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")


def detect_root(start: Path) -> Path | None:
    """Walk up from `start` looking for a .git directory. Returns None if not found."""
    for parent in [start] + list(start.parents):
        if (parent / ".git").exists():
            return parent
    return None


def resolve_image(link: str, md_path: Path, root: Path | None) -> tuple[Path | None, str]:
    """Return (resolved absolute path or None, rewritten link).

    External links (http/https/data) are kept as-is.
    If file can't be found, link is kept as-is and caller decides how to report.
    """
    if link.startswith(("http://", "https://", "data:")):
        return None, link

    # Strip optional title suffix:  path "title"
    path_part = link
    title_suffix = ""
    if ' "' in link:
        path_part, _, tail = link.partition(' "')
        title_suffix = ' "' + tail

    decoded = urllib.parse.unquote(path_part)
    decoded_path = Path(decoded)

    candidates: list[Path] = []
    if decoded_path.is_absolute():
        candidates.append(decoded_path)
    else:
        # Prefer the markdown file's directory
        candidates.append(md_path.parent / decoded_path)
        # Fall back to the root (e.g. vault root / git root) if available
        if root is not None:
            candidates.append(root / decoded_path)

    for candidate in candidates:
        if candidate.exists():
            absolute = candidate.resolve()
            try:
                rel = absolute.relative_to(md_path.parent.resolve())
                return absolute, str(rel) + title_suffix
            except ValueError:
                return absolute, str(absolute) + title_suffix

    return None, link


def normalize_markdown(md_path: Path, root: Path | None, dry_run: bool = False) -> tuple[int, int, list[str]]:
    text = md_path.read_text(encoding="utf-8")
    changes: list[str] = []
    fixed = 0
    broken = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal fixed, broken
        alt = match.group(1)
        original_link = match.group(2)
        resolved, new_link = resolve_image(original_link, md_path, root)

        if resolved is None:
            if original_link.startswith(("http://", "https://", "data:")):
                return match.group(0)
            broken += 1
            changes.append(f"  not found: {original_link}")
            return match.group(0)

        if new_link != original_link:
            fixed += 1
            changes.append(f"  rewrote: {original_link}\n      -> {new_link}")
        return f"![{alt}]({new_link})"

    new_text = IMG_PATTERN.sub(replace, text)

    if not dry_run and new_text != text:
        md_path.write_text(new_text, encoding="utf-8")

    return fixed, broken, changes


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Normalize markdown image paths for publish-tool compatibility."
    )
    parser.add_argument("file", help="Path to the markdown file")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview only, do not modify the file",
    )
    parser.add_argument(
        "--root",
        default=None,
        help="Root directory used as a fallback when resolving relative paths. "
             "Defaults to MD_VAULT_ROOT env var, or auto-detected git repo root.",
    )
    args = parser.parse_args()

    md_path = Path(args.file).expanduser().resolve()
    if not md_path.exists():
        print(f"file not found: {md_path}", file=sys.stderr)
        return 1

    root_arg = args.root or os.environ.get("MD_VAULT_ROOT")
    root = Path(root_arg).expanduser().resolve() if root_arg else detect_root(md_path.parent)

    fixed, broken, changes = normalize_markdown(md_path, root=root, dry_run=args.dry_run)

    print(f"scanned: {md_path.name}")
    if root:
        print(f"fallback root: {root}")
    for line in changes:
        print(line)
    if not changes:
        print("  (no images needed processing)")
    print()
    print(f"fixed: {fixed}  not-found: {broken}")
    if args.dry_run:
        print("(dry-run, file not modified)")

    return 0 if broken == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
