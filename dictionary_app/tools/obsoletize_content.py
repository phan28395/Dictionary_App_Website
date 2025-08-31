#!/usr/bin/env python3
import argparse
import os
import re
import shutil
import json
from typing import Dict, List, Optional, Set, Tuple

# This script builds a rough dependency graph by scanning source files for references
# (imports, includes, src/href, CSS url(), Django template tags) and identifies files
# that are not reachable from a set of seeds. Unreachable files can be moved to /obsoleted.


TEXT_EXTS = {".py", ".js", ".jsx", ".ts", ".tsx", ".json", ".html", ".htm", ".css", ".scss", ".yaml", ".yml"}
ASSET_EXTS = {".svg", ".png", ".jpg", ".jpeg", ".gif", ".ico", ".bmp", ".webp", ".ttf", ".otf", ".woff", ".woff2", ".eot", ".mp3", ".mp4"}
IGNORED_DIRS = {".git", "obsoleted", "node_modules", ".venv", "venv", "env", ".env", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".cache"}
ALWAYS_KEEP_DIRS = {"migrations"}  # heuristics: keep Django migrations by default

# Basic regexes for references
RE_PY_IMPORT = re.compile(r"^\s*(?:from\s+([\w\.]+)\s+import|import\s+([\w\.]+))", re.MULTILINE)
RE_JS_IMPORT = re.compile(r"(?:import\s+[^'\"\(]*from\s*['\"]([^'\"]+)['\"]|require\(\s*['\"]([^'\"]+)['\"]\s*\)|import\(\s*['\"]([^'\"]+)['\"]\s*\))")
RE_HTML_SRC_HREF = re.compile(r"(?:src|href)\s*=\s*['\"]([^'\"]+)['\"]", re.IGNORECASE)
RE_CSS_URL = re.compile(r"url\(\s*['\"]?([^'\")]+)['\"]?\s*\)")
RE_DJANGO_TPL = re.compile(r"\{\%\s*(?:include|extends)\s*['\"]([^'\"]+)['\"]\s*\%\}")
RE_DJANGO_STATIC = re.compile(r"static\(\s*['\"]([^'\"]+)['\"]\s*\)")


def norm(path: str) -> str:
    return path.replace(os.sep, "/")


def list_files(root: str) -> List[str]:
    files: List[str] = []
    for cur, dirs, fnames in os.walk(root):
        # prune ignored dirs
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        for f in fnames:
            files.append(os.path.join(cur, f))
    return files


def relpath(root: str, path: str) -> str:
    return norm(os.path.relpath(path, root))


def module_to_path(root: str, module: str, exts: Tuple[str, ...]) -> Optional[str]:
    # Map "a.b.c" -> a/b/c.py or a/b/c/__init__.py
    base = module.replace(".", "/")
    candidates = [f"{base}{ext}" for ext in exts] + [f"{base}/__init__{ext}" for ext in exts]
    for cand in candidates:
        p = os.path.join(root, cand)
        if os.path.isfile(p):
            return relpath(root, p)
    return None


def resolve_relative(importer_rel: str, spec: str, exts: Tuple[str, ...]) -> Optional[str]:
    # Resolve ./ and ../ specs relative to importer
    importer_dir = os.path.dirname(importer_rel)
    base = os.path.normpath(os.path.join(importer_dir, spec))
    # Check exact
    if os.path.splitext(base)[1]:
        if os.path.exists(base):
            return norm(base)
        return None
    # Try with extensions and index.*
    for ext in exts:
        cand = base + ext
        if os.path.exists(cand):
            return norm(cand)
    for ext in exts:
        cand = os.path.join(base, f"index{ext}")
        if os.path.exists(cand):
            return norm(cand)
    return None


def find_package_main(root: str) -> Optional[str]:
    pkg = os.path.join(root, "package.json")
    if not os.path.isfile(pkg):
        return None
    try:
        with open(pkg, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        main = data.get("main") or data.get("module") or None
        if isinstance(main, str):
            p = os.path.join(root, main)
            if os.path.exists(p):
                return relpath(root, p)
    except Exception:
        pass
    return None


def seed_candidates(root: str) -> Set[str]:
    seeds: Set[str] = set()
    for name in ("manage.py", "app.py", "wsgi.py", "asgi.py", "main.py"):
        p = os.path.join(root, name)
        if os.path.isfile(p):
            seeds.add(relpath(root, p))
    # HTML entry points
    for f in ("index.html", "public/index.html"):
        p = os.path.join(root, f)
        if os.path.isfile(p):
            seeds.add(relpath(root, p))
    # JS entry via package.json
    m = find_package_main(root)
    if m:
        seeds.add(m)
    return seeds


def parse_references(root: str, rel: str) -> Set[str]:
    path = os.path.join(root, rel)
    ext = os.path.splitext(path)[1].lower()
    refs: Set[str] = set()

    def add_if_exists(candidate_rel: str) -> None:
        if os.path.exists(os.path.join(root, candidate_rel)):
            refs.add(candidate_rel)

    try:
        if ext in TEXT_EXTS:
            with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                content = fh.read()
        else:
            return refs
    except Exception:
        return refs

    if ext == ".py":
        for m in RE_PY_IMPORT.finditer(content):
            mod = m.group(1) or m.group(2)
            if not mod:
                continue
            p = module_to_path(root, mod, (".py",))
            if p:
                refs.add(p)

        # Django templates referenced via render/template_name strings - heuristic
        for tpl in re.findall(r"['\"]([\w\-/]+\.(?:html|htm))['\"]", content):
            # search under templates/ for suffix match
            for dirpath, _, files in os.walk(root):
                if os.path.basename(dirpath) != "templates":
                    continue
                cand = os.path.join(dirpath, tpl)
                if os.path.isfile(cand):
                    refs.add(relpath(root, cand))

    if ext in {".js", ".jsx", ".ts", ".tsx"}:
        for m in RE_JS_IMPORT.finditer(content):
            spec = m.group(1) or m.group(2) or m.group(3)
            if not spec:
                continue
            if spec.startswith(("./", "../")):
                resolved = resolve_relative(rel, spec, (".js", ".jsx", ".ts", ".tsx", ".json"))
                if resolved:
                    refs.add(resolved)
            else:
                # Bare specifier -> likely dependency, ignore
                pass

    if ext in {".html", ".htm"}:
        for m in RE_HTML_SRC_HREF.finditer(content):
            href = m.group(1)
            if href.startswith(("http://", "https://", "//")):
                continue
            if href.startswith(("./", "../")):
                resolved = resolve_relative(rel, href, tuple(TEXT_EXTS | ASSET_EXTS))
                if resolved:
                    refs.add(resolved)
            else:
                # Try relative to file and project root
                for base in (os.path.dirname(rel), "."):
                    cand = norm(os.path.normpath(os.path.join(base, href)))
                    add_if_exists(cand)
        for m in RE_DJANGO_TPL.finditer(content):
            tpl = m.group(1)
            # Look up under any templates dir
            for dirpath, _, _ in os.walk(root):
                if os.path.basename(dirpath) != "templates":
                    continue
                cand = os.path.join(dirpath, tpl)
                if os.path.isfile(cand):
                    refs.add(relpath(root, cand))

    if ext in {".css", ".scss"}:
        for m in RE_CSS_URL.finditer(content):
            url = m.group(1)
            if url.startswith(("data:", "http://", "https://", "//")):
                continue
            resolved = None
            if url.startswith(("./", "../")):
                resolved = resolve_relative(rel, url, tuple(ASSET_EXTS | TEXT_EXTS))
            else:
                # relative to file
                cand = norm(os.path.normpath(os.path.join(os.path.dirname(rel), url)))
                if os.path.exists(os.path.join(root, cand)):
                    resolved = cand
            if resolved:
                refs.add(resolved)

    # Django static('path') anywhere
    for m in RE_DJANGO_STATIC.finditer(content):
        asset = m.group(1)
        # Look up under static/ dirs
        for dirpath, _, _ in os.walk(root):
            if os.path.basename(dirpath) != "static":
                continue
            cand = os.path.join(dirpath, asset)
            if os.path.isfile(cand):
                refs.add(relpath(root, cand))

    return refs


def build_graph(root: str, files: List[str]) -> Tuple[Dict[str, Set[str]], Set[str]]:
    rels = [relpath(root, f) for f in files]
    # Exclude always-keep dirs
    keep_prefixes = tuple(f"{d}/" for d in ALWAYS_KEEP_DIRS)
    filtered = [r for r in rels if not any(r.startswith(pref) or f"/{pref}" in r for pref in keep_prefixes)]

    graph: Dict[str, Set[str]] = {r: set() for r in rels}
    for r in rels:
        refs = parse_references(root, r)
        # Only keep edges to files we know about
        graph[r] = {ref for ref in refs if ref in graph}
    return graph, set(rels)


def reachable(graph: Dict[str, Set[str]], seeds: Set[str]) -> Set[str]:
    seen: Set[str] = set()
    stack: List[str] = list(seeds)
    while stack:
        cur = stack.pop()
        if cur in seen:
            continue
        seen.add(cur)
        for nxt in graph.get(cur, ()):  # type: ignore
            if nxt not in seen:
                stack.append(nxt)
    return seen


def move_to_obsoleted(root: str, paths: List[str], apply: bool) -> None:
    obsoleted = os.path.join(root, "obsoleted")
    os.makedirs(obsoleted, exist_ok=True)
    for r in paths:
        src = os.path.join(root, r)
        dst = os.path.join(obsoleted, r)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if apply:
            shutil.move(src, dst)
        print(("Moved" if apply else "Would move"), r, "->", norm(os.path.relpath(dst, root)))


def main() -> None:
    ap = argparse.ArgumentParser(description="Content-aware obsoleted file finder/mover")
    ap.add_argument("--root", default=".", help="Project root (default: .)")
    ap.add_argument("--seed", action="append", default=[], help="Seed file(s) relative to root; can repeat")
    ap.add_argument("--auto-seed", action="store_true", help="Auto-detect common entry points (manage.py, index.html, package.json main)")
    ap.add_argument("--apply", action="store_true", help="Apply moves (default: dry run)")
    ap.add_argument("--keep-ext", action="append", default=[], help="Always keep files with these extensions (e.g. --keep-ext .md)")
    ap.add_argument("--keep-path", action="append", default=[], help="Always keep any path containing this fragment (repeatable)")
    ap.add_argument("--print-seeds", action="store_true", help="Print resolved seeds")
    args = ap.parse_args()

    root = os.path.abspath(args.root)
    all_files_abs = list_files(root)
    all_files_rel = [relpath(root, f) for f in all_files_abs]

    seeds: Set[str] = set()
    for s in args.seed:
        p = os.path.join(root, s)
        if os.path.exists(p):
            seeds.add(relpath(root, p))
        else:
            print("Seed not found:", s)
    if args.auto_seed or not seeds:
        seeds |= seed_candidates(root)

    if args.print_seeds:
        print("Seeds:")
        for s in sorted(seeds):
            print(" -", s)

    graph, nodes = build_graph(root, all_files_abs)
    keep_by_ext = {e.lower() for e in args.keep_ext}

    # Always keep seeds, and anything outside TEXT/ASSET_EXTS (unknown types)
    reachable_nodes = reachable(graph, seeds)
    unused = []
    for n in sorted(nodes):
        if n in reachable_nodes:
            continue
        ext = os.path.splitext(n)[1].lower()
        if keep_by_ext and ext in keep_by_ext:
            continue
        if any(k in n for k in args.keep_path):
            continue
        # Skip files in always-keep dirs
        if any(part in ALWAYS_KEEP_DIRS for part in n.split("/")):
            continue
        # Skip non-text/asset files cautiously by default
        if ext not in TEXT_EXTS | ASSET_EXTS:
            continue
        unused.append(n)

    if not unused:
        print("No unused files detected by content analysis.")
        return

    print(f"Detected {len(unused)} unused file(s):")
    for u in unused:
        print(" -", u)

    move_to_obsoleted(root, unused, apply=args.apply)
    if args.apply:
        print("Done. Review 'obsoleted' directory. Restore as needed.")


if __name__ == "__main__":
    main()

