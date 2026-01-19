# Copyright (c) 2026 Robin Mordasiewicz. MIT License.

"""Tag-based version calculation utility.

Eliminates file-based versioning race conditions by deriving version from git tags.
This is the single source of truth for version calculation across all scripts.
"""

import re
import subprocess


def get_version_from_tags() -> str:
    """Calculate version from latest git tag.

    Returns the semantic version from the most recent git tag,
    stripping the 'v' prefix if present.

    Returns:
        Version string in semver format (e.g., "2.0.38").
        Returns "0.0.0" if no tags exist or git fails.
    """
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
        tag = result.stdout.strip()
        # Strip 'v' prefix: v2.0.38 -> 2.0.38
        return tag.lstrip("v") if tag.startswith("v") else tag
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return "0.0.0"


def calculate_next_version(current: str, bump_type: str) -> str:
    """Calculate next semantic version based on bump type.

    Args:
        current: Current version string (e.g., "2.0.38").
        bump_type: One of "major", "minor", or "patch".

    Returns:
        Next version string according to semver rules.
        Returns "1.0.0" if current version is invalid.
    """
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)$", current)
    if not match:
        return "1.0.0"

    major, minor, patch = map(int, match.groups())

    if bump_type == "major":
        return f"{major + 1}.0.0"
    if bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    # Default: patch bump
    return f"{major}.{minor}.{patch + 1}"


def is_valid_semver(version: str) -> bool:
    """Check if a version string is valid semver format.

    Args:
        version: Version string to validate.

    Returns:
        True if valid semver (X.Y.Z where X, Y, Z are integers).
    """
    return bool(re.match(r"^\d+\.\d+\.\d+$", version))


def get_version() -> str:
    """Get current version - alias for get_version_from_tags.

    This function provides backward compatibility for scripts that
    previously read from .version file.

    Returns:
        Current version from git tags.
    """
    return get_version_from_tags()
