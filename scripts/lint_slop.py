#!/usr/bin/env python3
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Banned characters
EM_DASH = "\u2014"
EMOJI_PATTERN = re.compile(r"[\U0001F300-\U0001FAFF\u2600-\u27BF\uFE0F]")

# Banned buzzwords (case-insensitive)
BANNED_WORDS = [
    "seamless", "revolutioniz", "cutting-edge", "state-of-the-art",
    "next-gen", "unlock", "supercharge", "empower", "elevate",
    "leverage", "harness", "game-changer", "delve", "effortless",
    "reimagine", "world-class", "in today's"
]

# Fake markers
FAKE_MARKERS = [
    "lorem", "john doe", "example.com", "trusted by", "testimonial",
    "customers", "star ratings"
]

# Disallowed CSS patterns
DISALLOWED_CSS = [
    (re.compile(r"border-radius\s*:\s*([2-9][4-9]|[3-9]\d|\d{3,})px"), "Radius >= 24px on controls"),
    (re.compile(r"cursor\s*:\s*url\("), "Custom cursor with url()"),
]

# Disallowed JS patterns
DISALLOWED_JS = [
    "intersectionobserver", "scroll-timeline", "animation-timeline", "parallax"
]

SCAN_EXTENSIONS = {".py", ".css", ".js", ".html", ".svg", ".md"}
SCAN_DIRS = ["ui", "static", "docs"]
SCAN_FILES = ["app.py", "README.md"]


def check_file(path: Path) -> list:
    errors = []
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        return [f"Could not read {path}: {e}"]

    # Check for em dash
    if EM_DASH in content:
        # report line numbers
        for idx, line in enumerate(content.splitlines(), start=1):
            if EM_DASH in line:
                errors.append(f"{path}:{idx} contains em dash (U+2014)")

    # Check for emoji
    for idx, line in enumerate(content.splitlines(), start=1):
        if EMOJI_PATTERN.search(line):
            errors.append(f"{path}:{idx} contains banned emoji character")

    # Check banned words
    content_lower = content.lower()
    for word in BANNED_WORDS:
        if word in content_lower:
            # find line
            for idx, line in enumerate(content.splitlines(), start=1):
                if word in line.lower():
                    errors.append(f"{path}:{idx} contains banned word '{word}'")

    # Check fake markers
    for marker in FAKE_MARKERS:
        if marker in content_lower:
            for idx, line in enumerate(content.splitlines(), start=1):
                if marker in line.lower():
                    errors.append(f"{path}:{idx} contains fake marker '{marker}'")

    # CSS specific checks
    if path.suffix == ".css":
        for pattern, desc in DISALLOWED_CSS:
            for idx, line in enumerate(content.splitlines(), start=1):
                if pattern.search(line):
                    errors.append(f"{path}:{idx} CSS violation: {desc}")
        # check gradient outside .skeleton
        for idx, line in enumerate(content.splitlines(), start=1):
            if "gradient(" in line and ".skeleton" not in line and "linear-gradient" in line:
                # check if enclosed in a skeleton rule
                errors.append(f"{path}:{idx} gradient outside .skeleton rule")

    # JS specific checks
    if path.suffix == ".js":
        for kw in DISALLOWED_JS:
            if kw in content_lower:
                for idx, line in enumerate(content.splitlines(), start=1):
                    if kw in line.lower():
                        errors.append(f"{path}:{idx} JS violation: {kw}")

    return errors


def check_required_assets() -> list:
    errors = []
    # Required: static/favicon.png, static/favicon.svg
    fav_svg = ROOT / "static" / "favicon.svg"
    fav_png = ROOT / "static" / "favicon.png"
    if not fav_svg.exists():
        errors.append("Missing required static/favicon.svg")
    if not fav_png.exists():
        errors.append("Missing required static/favicon.png")

    config_path = ROOT / ".streamlit" / "config.toml"
    if not config_path.exists():
        errors.append("Missing .streamlit/config.toml")
    else:
        cfg = config_path.read_text(encoding="utf-8")
        if 'toolbarMode = "minimal"' not in cfg:
            errors.append('.streamlit/config.toml missing toolbarMode = "minimal"')
        if "gatherUsageStats = false" not in cfg:
            errors.append('.streamlit/config.toml missing gatherUsageStats = false')

    return errors


def main():
    all_errors = []
    # Collect files to scan
    target_files = []
    for f in SCAN_FILES:
        p = ROOT / f
        if p.exists():
            target_files.append(p)

    for d in SCAN_DIRS:
        dp = ROOT / d
        if dp.exists():
            for root_dir, _, files in os.walk(dp):
                for file in files:
                    fp = Path(root_dir) / file
                    if fp.suffix in SCAN_EXTENSIONS:
                        target_files.append(fp)

    for target in target_files:
        errs = check_file(target)
        all_errors.extend(errs)

    all_errors.extend(check_required_assets())

    if all_errors:
        print(f"LINT FAILED ({len(all_errors)} errors):")
        for err in all_errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("LINT PASSED: 0 slop violations detected.")
        sys.exit(0)


if __name__ == "__main__":
    main()
