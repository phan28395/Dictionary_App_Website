#!/usr/bin/env python3
import argparse
import hashlib
import os
from pathlib import Path
from typing import List, Tuple, Set


def sha256sum(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def list_files(root: Path) -> List[Path]:
    files: List[Path] = []
    for base, _dirs, fnames in os.walk(root):
        b = Path(base)
        for name in fnames:
            files.append(b / name)
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description="Delete files outside of 'obsoleted' that duplicate files inside it.")
    parser.add_argument('--root', type=Path, default=Path.cwd(), help='Repository root (default: current directory)')
    parser.add_argument('--obsoleted', type=Path, default=None, help="Obsoleted directory (default: <root>/obsoleted)")
    parser.add_argument('--mode', choices=['relative', 'filename'], default='relative',
                        help="Match strategy: 'relative' matches by relative path; 'filename' matches by basename only.")
    parser.add_argument('--verify-hash', action='store_true', help='Only delete when file contents are identical (SHA-256).')
    parser.add_argument('--dry-run', action='store_true', help='Print actions without deleting files.')
    parser.add_argument('--case-insensitive', action='store_true', help='Case-insensitive filename matching (useful on Windows).')

    args = parser.parse_args()
    root: Path = args.root.resolve()
    obsoleted: Path = (args.obsoleted or (root / 'obsoleted')).resolve()

    if not obsoleted.exists() or not obsoleted.is_dir():
        print(f"Error: obsoleted directory not found at: {obsoleted}")
        return 2

    # Gather files inside obsoleted
    inner: List[Tuple[Path, Path]] = []  # (absolute_path, relative_to_obsoleted)
    for base, _dirs, fnames in os.walk(obsoleted):
        b = Path(base)
        for name in fnames:
            abs_path = b / name
            rel_path = abs_path.relative_to(obsoleted)
            inner.append((abs_path, rel_path))

    # Build candidate deletions
    to_delete: List[Tuple[Path, Path]] = []  # (outside_path, matching_obsoleted_path)

    if args.mode == 'relative':
        for abs_in, rel_in in inner:
            outside = root / rel_in
            try:
                outside_resolved = outside.resolve()
            except FileNotFoundError:
                continue
            # Ensure we don't target files inside obsoleted
            if not outside_resolved.exists() or obsoleted in outside_resolved.parents:
                continue
            if args.verify-hash:
                try:
                    if sha256sum(abs_in) != sha256sum(outside_resolved):
                        continue
                except FileNotFoundError:
                    continue
            to_delete.append((outside_resolved, abs_in))
    else:  # filename mode
        # Build set/map of basenames within obsoleted
        if args.case_insensitive:
            names: Set[str] = {p.name.lower() for _abs, p in inner}
        else:
            names = {p.name for _abs, p in inner}

        # Scan all files outside obsoleted
        for base, _dirs, fnames in os.walk(root):
            b = Path(base)
            # Skip obsoleted subtree
            try:
                if obsoleted == b or obsoleted in b.parents:
                    continue
            except RuntimeError:
                # On some platforms Path.parents may raise for odd paths; ignore
                pass
            for name in fnames:
                candidate = b / name
                key = name.lower() if args.case_insensitive else name
                if key not in names:
                    continue
                if args.verify-hash:
                    # Find any inner file(s) with same name and compare hashes; delete only if any match
                    try:
                        cand_hash = sha256sum(candidate)
                    except FileNotFoundError:
                        continue
                    matched = False
                    for abs_in, rel_in in inner:
                        if (rel_in.name.lower() if args.case_insensitive else rel_in.name) == key:
                            try:
                                if sha256sum(abs_in) == cand_hash:
                                    matched = True
                                    break
                            except FileNotFoundError:
                                continue
                    if not matched:
                        continue
                to_delete.append((candidate.resolve(), obsoleted / key))

    # Deduplicate targets
    seen: Set[Path] = set()
    unique: List[Tuple[Path, Path]] = []
    for out_path, in_path in to_delete:
        if out_path not in seen:
            seen.add(out_path)
            unique.append((out_path, in_path))

    if not unique:
        print("No external duplicates found to delete.")
        return 0

    print(f"Planned deletions ({len(unique)}):")
    for out_path, in_path in unique:
        print(f"DELETE {out_path}")

    if args.dry_run:
        print("Dry run complete. No files were deleted.")
        return 0

    # Perform deletions
    errors = 0
    for out_path, _ in unique:
        try:
            out_path.unlink()
        except Exception as e:
            print(f"Failed to delete {out_path}: {e}")
            errors += 1

    if errors:
        print(f"Completed with {errors} error(s).")
        return 1
    print("Deletion complete.")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

