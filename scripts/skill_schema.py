"""Canonical skill frontmatter contract — stdlib only (no third-party deps).

Tolerant on read (coercion, inference), strict on emit. All skill-file format
variation is absorbed here so the published catalog is uniform. See
biopb-mcp/docs/skill-interface.md (in the biopb repo) §1 and §5.

Kept dependency-free on purpose: the docs toolchain should need only PyYAML to
build the catalog, nothing heavier.
"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field

# Schema of catalog.json. Bump only on a breaking change; the MCP server guards
# on this and fails open (keeps last-good / bundled) on an unknown value.
CATALOG_VERSION = 1

# Current authoring dialect. Older skill files declare a lower spec_version and are
# up-converted by migrate() in the build script, so the emitted catalog is uniform.
CURRENT_SPEC_VERSION = 1

# Controlled tag vocabulary. Unknown tags fail `--check`, keeping the taxonomy
# curated. Grow this deliberately via PR.
ALLOWED_TAGS = {
    "segmentation", "detection", "restoration", "super-resolution",
    "measurement", "io", "visualization", "annotation", "ops", "tensor",
    "cellpose", "workflow",
}

SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
KEBAB = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


@dataclass
class CatalogEntry:
    """What the build EMITS per skill — strict and canonical."""

    id: str
    title: str
    description: str
    tags: list
    version: str
    spec_version: int
    requires: list
    updated: str          # ISO date, derived from git (never author-supplied)
    url: str
    sha256: str

    def to_dict(self) -> dict:
        return asdict(self)


def coerce_list(v) -> list:
    """Accept a list, a comma-separated string, a scalar, or None."""
    if v is None:
        return []
    if isinstance(v, list):
        return v
    if isinstance(v, str):
        return [s.strip() for s in v.split(",") if s.strip()]
    return [v]
