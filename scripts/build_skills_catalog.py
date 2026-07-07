#!/usr/bin/env python3
"""Normalize, validate, and index skills/*.md into skills/catalog.json.

This is the single choke point for skill-file format variation
(docs/skill-interface.md §5): tolerant read -> strict, canonical, versioned emit.

Usage:
    python scripts/build_skills_catalog.py            # generate skills/catalog.json
    python scripts/build_skills_catalog.py --check     # validate only (CI gate)

Warnings never fail the build; ERRORS do (non-zero exit, catalog not written).
Only third-party dependency: PyYAML.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from skill_schema import (  # noqa: E402
    ALLOWED_TAGS, CATALOG_VERSION, CURRENT_SPEC_VERSION, KEBAB, SEMVER,
    CatalogEntry, coerce_list,
)

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
CATALOG = SKILLS_DIR / "catalog.json"
SITE_BASE = "https://biopb.org/skills"
_FRONTMATTER = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)

errors: list[str] = []
warnings: list[str] = []


def err(fname: str, msg: str) -> None:
    errors.append(f"ERROR {fname}: {msg}")


def warn(fname: str, msg: str) -> None:
    warnings.append(f"warn  {fname}: {msg}")


def split_frontmatter(text: str, fname: str):
    m = _FRONTMATTER.match(text.replace("\r\n", "\n"))
    if not m:
        err(fname, "missing or malformed YAML frontmatter (--- ... ---)")
        return None, ""
    try:
        return yaml.safe_load(m.group(1)) or {}, m.group(2)
    except yaml.YAMLError as e:
        err(fname, f"YAML parse error: {e}")
        return None, ""


def migrate(fm: dict, fname: str) -> dict:
    """Up-convert older authoring dialects to CURRENT_SPEC_VERSION."""
    sv = int(fm.get("spec_version", 1) or 1)
    if sv > CURRENT_SPEC_VERSION:
        warn(fname, f"spec_version {sv} newer than supported {CURRENT_SPEC_VERSION}")
    # Example future hook:
    # if sv < 2: fm = _v1_to_v2(fm); fm["spec_version"] = 2
    fm["spec_version"] = min(sv, CURRENT_SPEC_VERSION)
    return fm


def git_updated(path: Path) -> str:
    """Last-commit date (author-independent). Falls back to today if uncommitted."""
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", path.name],
            capture_output=True, text=True, cwd=path.parent, check=True,
        ).stdout.strip()
        if out:
            return out
    except Exception:
        pass
    return datetime.now(timezone.utc).date().isoformat()


def first_h1(body: str) -> str | None:
    for line in body.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None


def process(path: Path) -> CatalogEntry | None:
    fname = path.name
    stem = path.stem
    raw = path.read_text(encoding="utf-8")
    fm, body = split_frontmatter(raw, fname)
    if fm is None:
        return None
    if not isinstance(fm, dict):
        err(fname, "frontmatter is not a mapping")
        return None

    fm = migrate(fm, fname)

    # --- inference / coercion (tolerant read) ---
    if not _stem_ok(stem, fname):
        return None
    fm.setdefault("id", stem)
    if fm["id"] != stem:
        err(fname, f"id {fm['id']!r} must equal filename stem {stem!r}")

    description = (fm.get("description") or "").strip()
    if not description:
        err(fname, "missing required field: description")
        return None

    title = (fm.get("title") or "").strip()
    if not title:
        title = first_h1(body) or stem.replace("-", " ").title()
        warn(fname, "title inferred (add an explicit `title:`)")

    tags = [t.lower() for t in coerce_list(fm.get("tags"))]
    bad = sorted(set(tags) - ALLOWED_TAGS)
    if bad:
        err(fname, f"unknown tag(s) {bad}; allowed: {sorted(ALLOWED_TAGS)}")

    version = str(fm.get("version") or "0.0.0")
    if not SEMVER.match(version):
        err(fname, f"version must be MAJOR.MINOR.PATCH, got {version!r}")

    requires = [str(r) for r in coerce_list(fm.get("requires"))]

    if not body.strip():
        err(fname, "empty body")
    elif not first_h1(body):
        warn(fname, "body has no H1 heading")

    if errors:  # don't emit an entry built from invalid input
        return None

    return CatalogEntry(
        id=fm["id"], title=title, description=description, tags=tags,
        version=version, spec_version=int(fm["spec_version"]), requires=requires,
        updated=git_updated(path), url=f"{SITE_BASE}/{fname}",
        sha256=hashlib.sha256(raw.encode("utf-8")).hexdigest(),
    )


def _stem_ok(stem: str, fname: str) -> bool:
    if not KEBAB.match(stem):
        err(fname, f"filename stem {stem!r} must be kebab-case")
        return False
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="validate only; do not write catalog.json")
    args = ap.parse_args()

    if not SKILLS_DIR.is_dir():
        print(f"No skills directory at {SKILLS_DIR}", file=sys.stderr)
        return 1

    entries: list[CatalogEntry] = []
    seen: set[str] = set()
    for path in sorted(SKILLS_DIR.glob("*.md")):
        entry = process(path)
        if entry is None:
            continue
        if entry.id in seen:
            err(path.name, f"duplicate id {entry.id!r}")
            continue
        seen.add(entry.id)
        entries.append(entry)

    for w in warnings:
        print(w, file=sys.stderr)
    for e in errors:
        print(e, file=sys.stderr)
    if errors:
        print(f"\n{len(errors)} error(s); catalog NOT written.", file=sys.stderr)
        return 1

    if args.check:
        print(f"OK - {len(entries)} skill(s) valid ({len(warnings)} warning(s)).")
        return 0

    catalog = {
        "catalog_version": CATALOG_VERSION,
        "generated": datetime.now(timezone.utc)
            .isoformat(timespec="seconds").replace("+00:00", "Z"),
        "skills": [e.to_dict() for e in entries],
    }
    CATALOG.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {CATALOG} ({len(entries)} skill(s), {len(warnings)} warning(s)).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
