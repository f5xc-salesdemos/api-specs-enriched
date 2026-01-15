#!/usr/bin/env python3
"""Utility to convert long YAML string values to folded blocks.

This script converts long YAML string values (>120 chars) to folded blocks (using '>') to comply with yamllint line-length requirements.

Usage:
    python -m scripts.utils.format_yaml_descriptions <yaml_file> [--max-line-length 100] [--dry-run]
"""

import argparse
import sys
from pathlib import Path

import yaml


def wrap_text(text: str, max_width: int = 100) -> list[str]:
    """Wrap text to specified width, preserving word boundaries.

    Args:
        text: The text to wrap
        max_width: Maximum width per line (default: 100)

    Returns:
        List of wrapped lines
    """
    # Preserve multiple spaces and special characters
    words = text.split()
    lines: list[str] = []
    current_line: list[str] = []
    current_length = 0

    for word in words:
        word_length = len(word)
        # +1 for the space
        if current_length + word_length + (1 if current_line else 0) <= max_width:
            current_line.append(word)
            current_length += word_length + (1 if current_line else 0)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
            current_length = word_length

    if current_line:
        lines.append(" ".join(current_line))

    return lines


def convert_long_strings_to_folded_blocks(
    data: dict | list,
    max_line_length: int = 120,
    wrap_width: int = 100,
    _path: str = "",
) -> dict | list:
    """Recursively convert long string values to folded blocks.

    Args:
        data: YAML data structure (dict or list)
        max_line_length: Threshold for converting strings (default: 120)
        wrap_width: Width to wrap lines to (default: 100)
        _path: Current path in data structure (for debugging)

    Returns:
        Modified data structure with long strings as folded blocks
    """
    if isinstance(data, dict):
        result: dict[str, str | dict | list] = {}
        for key, value in data.items():
            current_path = f"{_path}.{key}" if _path else key

            if isinstance(value, str) and len(value) > max_line_length:
                # Convert to folded block using yaml.scalarstring.FoldedScalarString
                wrapped_lines = wrap_text(value, wrap_width)
                # Join with newlines for folded block representation
                result[key] = "\n".join(wrapped_lines)
            elif isinstance(value, (dict, list)):
                result[key] = convert_long_strings_to_folded_blocks(
                    value,
                    max_line_length,
                    wrap_width,
                    current_path,
                )
            else:
                result[key] = value

        return result

    if isinstance(data, list):
        return [
            (
                convert_long_strings_to_folded_blocks(
                    item,
                    max_line_length,
                    wrap_width,
                    f"{_path}[{i}]",
                )
                if isinstance(item, (dict, list))
                else "\n".join(wrap_text(item, wrap_width))
                if isinstance(item, str) and len(item) > max_line_length
                else item
            )
            for i, item in enumerate(data)
        ]

    return data


class FoldedScalarString(str):
    """Custom string class to indicate folded scalar representation."""


def folded_scalar_representer(dumper: yaml.Dumper, data: str) -> yaml.ScalarNode:
    """Custom representer for folded scalar strings."""
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style=">")


def convert_yaml_file(
    yaml_file: Path,
    max_line_length: int = 120,
    wrap_width: int = 100,
    dry_run: bool = False,
) -> tuple[int, int]:
    """Convert long strings in a YAML file to folded blocks.

    Args:
        yaml_file: Path to the YAML file
        max_line_length: Threshold for converting strings (default: 120)
        wrap_width: Width to wrap lines to (default: 100)
        dry_run: If True, don't write changes (default: False)

    Returns:
        Tuple of (strings_converted, total_strings_checked)
    """
    # Read YAML file
    with open(yaml_file) as f:
        data = yaml.safe_load(f)

    # Convert long strings
    converted_data = convert_long_strings_to_folded_blocks(data, max_line_length, wrap_width)

    # Count conversions
    strings_converted = _count_long_strings(data, max_line_length)
    total_strings = _count_all_strings(data)

    if not dry_run:
        # Register custom representer for folded scalars
        yaml.add_representer(FoldedScalarString, folded_scalar_representer)

        # Write back to file with folded blocks
        with open(yaml_file, "w") as f:
            yaml.dump(
                converted_data,
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
                width=120,  # YAML dumper line width
            )

    return strings_converted, total_strings


def _count_long_strings(data: dict | list, max_length: int) -> int:
    """Count strings exceeding max_length."""
    count = 0
    if isinstance(data, dict):
        for value in data.values():
            if isinstance(value, str) and len(value) > max_length:
                count += 1
            elif isinstance(value, (dict, list)):
                count += _count_long_strings(value, max_length)
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, str) and len(item) > max_length:
                count += 1
            elif isinstance(item, (dict, list)):
                count += _count_long_strings(item, max_length)
    return count


def _count_all_strings(data: dict | list) -> int:
    """Count all strings in data structure."""
    count = 0
    if isinstance(data, dict):
        for value in data.values():
            if isinstance(value, str):
                count += 1
            elif isinstance(value, (dict, list)):
                count += _count_all_strings(value)
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, str):
                count += 1
            elif isinstance(item, (dict, list)):
                count += _count_all_strings(item)
    return count


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Convert long YAML string values to folded blocks",
    )
    parser.add_argument("yaml_file", type=Path, help="YAML file to process")
    parser.add_argument(
        "--max-line-length",
        type=int,
        default=120,
        help="Threshold for converting strings (default: 120)",
    )
    parser.add_argument(
        "--wrap-width",
        type=int,
        default=100,
        help="Width to wrap lines to (default: 100)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't write changes, just report what would be done",
    )

    args = parser.parse_args()

    if not args.yaml_file.exists():
        print(f"❌ Error: File not found: {args.yaml_file}", file=sys.stderr)
        return 1

    print(f"Processing {args.yaml_file}...")

    try:
        converted, total = convert_yaml_file(
            args.yaml_file,
            max_line_length=args.max_line_length,
            wrap_width=args.wrap_width,
            dry_run=args.dry_run,
        )

        if args.dry_run:
            print(f"🔍 Dry run: Would convert {converted} of {total} strings")
        else:
            print(f"✅ Converted {converted} of {total} strings to folded blocks")

        return 0

    except Exception as e:
        print(f"❌ Error processing file: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
