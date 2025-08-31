#!/usr/bin/env python3
import argparse
import fnmatch
import os
import shutil
from typing import Iterable, List, Set, Tuple


SAFE_DIR_PATTERNS = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".cache",
    ".tox",
    ".coverage_html",
    ".gradle",
    "coverage_html",
}

SAFE_FILE_PATTERNS = {
    "*.log",
    "*.tmp",
    "*.temp",
    "*.bak",
    "*.old",
    "*.orig",
    "*.swp",
    "*.swo",
    "*~",
    ".DS_Store",
    "Thumbs.db",
}

AGGRESSIVE_DIR_PATTERNS = {
    "dist",
    "build",
    "out",
    ".next",
    ".nuxt",
    "coverage",
    "node_modules",
    ".parcel-cache",
    ".webpack-cache",
    ".vite",
}

AGGRESSIVE_FILE_PATTERNS = {
    "*.map",
}

DEFAULT_EXCLUDES = {
    ".git",
    ".svn",
    ".hg",
    ".venv",
    "venv",
    "env",
    ".env",
    "obsoleted",
}


def build_patterns(aggressive: bool, include: Iterable[str]) -> Tuple[Set[str], Set[str]]:
    dir_patterns = set(SAFE_DIR_PATTERNS)
    file_patterns = set(SAFE_FILE_PATTERNS)
    if aggressive:
        dir_patterns.update(AGGRESSIVE_DIR_PATTERNS)
        file_patterns.update(AGGRESSIVE_FILE_PATTERNS)
    for pat in include:
        pat = pat.strip()
        if not pat:
            continue
        # Heuristic: treat patterns with a path separator as dir patterns if they don't contain a glob
        if os.sep in pat and not any(ch in pat for ch in "*?["):
            dir_patterns.add(pat)
        elif pat.endswith(os.sep):
            dir_patterns.add(pat.rstrip(os.sep))
        else:
            # If it looks like an extension or contains glob chars, add to file patterns
            file_patterns.add(pat)
    return dir_patterns, file_patterns


def should_exclude(path_parts: List[str], excludes: Set[str]) -> bool:
    return any(part in excludes for part in path_parts)


def matches_any(name: str, patterns: Set[str]) -> bool:
    return any(fnmatch.fnmatch(name, pat) for pat in patterns)


def collect_candidates(root: str, dir_patterns: Set[str], file_patterns: Set[str], excludes: Set[str]) -> Tuple[List[str], List[str]]:
    dir_candidates: List[str] = []
    file_candidates: List[str] = []
    for current_root, dirs, files in os.walk(root):
        rel_root = os.path.relpath(current_root, root)
        root_parts = [] if rel_root == "." else rel_root.split(os.sep)

        # Filter dirs in-place to avoid walking excluded trees
        kept_dirs = []
        for d in dirs:
            parts = root_parts + [d]
            if should_exclude(parts, excludes):
                continue
            # Directory matches if its name matches a pattern exactly or via glob
            if d in dir_patterns or matches_any(d, dir_patterns):
                dir_candidates.append(os.path.join(current_root, d))
                # Do not descend into it
                continue
            kept_dirs.append(d)
        dirs[:] = kept_dirs

        for f in files:
            parts = root_parts + [f]
            if should_exclude(parts, excludes):
                continue
            if matches_any(f, file_patterns):
                file_candidates.append(os.path.join(current_root, f))
    return dir_candidates, file_candidates


def move_path_to_obsoleted(root: str, obsoleted_root: str, path: str, dry_run: bool, verbose: bool) -> None:
    rel = os.path.relpath(path, root)
    dest = os.path.join(obsoleted_root, rel)
    if verbose:
        action = "Would move" if dry_run else "Moving"
        print(f"{action}: {rel} -> obsoleted/{rel}")
    if dry_run:
        return
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.move(path, dest)


def main() -> None:
    parser = argparse.ArgumentParser(description="Move likely obsolete files and directories into /obsoleted.")
    parser.add_argument("--root", default=".", help="Project root to scan (default: current directory)")
    parser.add_argument("--apply", action="store_true", help="Apply changes (otherwise run in dry-run mode)")
    parser.add_argument("--aggressive", action="store_true", help="Include build and dependency caches (dist, build, coverage, node_modules, etc.)")
    parser.add_argument("--include", default="", help="Additional comma-separated glob patterns to include")
    parser.add_argument("--exclude", default="", help="Comma-separated directory or file names to exclude")
    parser.add_argument("--verbose", action="store_true", help="Print detailed actions")
    args = parser.parse_args()

    root = os.path.abspath(args.root)
    obsoleted_root = os.path.join(root, "obsoleted")

    include = [s for s in (p.strip() for p in args.include.split(",")) if s]
    dir_patterns, file_patterns = build_patterns(args.aggressive, include)

    excludes: Set[str] = set(DEFAULT_EXCLUDES)
    if args.exclude:
        excludes.update(s.strip() for s in args.exclude.split(",") if s.strip())

    if args.verbose:
        print("Scanning root:", root)
        print("Obsoleted folder:", obsoleted_root)
        print("Dir patterns:", sorted(dir_patterns))
        print("File patterns:", sorted(file_patterns))
        print("Excludes:", sorted(excludes))

    dir_candidates, file_candidates = collect_candidates(root, dir_patterns, file_patterns, excludes)

    if not dir_candidates and not file_candidates:
        print("No candidates found.")
        return

    print(f"Found {len(dir_candidates)} dir(s) and {len(file_candidates)} file(s) to move.")
    if not args.apply:
        print("Dry-run mode. Use --apply to perform moves.")

    for d in sorted(dir_candidates):
        move_path_to_obsoleted(root, obsoleted_root, d, dry_run=not args.apply, verbose=args.verbose)

    for f in sorted(file_candidates):
        move_path_to_obsoleted(root, obsoleted_root, f, dry_run=not args.apply, verbose=args.verbose)

    if args.apply:
        print("Done. Review contents under 'obsoleted' and restore if needed.")


if __name__ == "__main__":
    main()

