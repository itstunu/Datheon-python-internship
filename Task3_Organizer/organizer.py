# organizer.py
"""
File Organizer - Datheon Python Internship, Task 3
==================================================

Sorts the files in a cluttered directory into category sub-folders
(Documents, Images, Videos, Archives, Code, Music, Other) based on file
extension.

Safety features
---------------
* Only top-level FILES are moved - sub-folders, symlinks and hidden
  dot-files (e.g. .gitignore) are skipped.
* Name collisions never overwrite: report.pdf -> report_1.pdf, report_2.pdf ...
* Every file is handled in its own try/except, so one bad file can never
  abort the whole run.
* --dry-run previews everything without touching the disk.

Usage
-----
    python organizer.py <directory>
    python organizer.py <directory> --dry-run
"""

import argparse
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

# Category -> set of extensions (lowercase, with leading dot).
EXTENSION_MAP = {
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".csv", ".xlsx", ".pptx", ".odt", ".rtf", ".md"},
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp", ".bmp"},
    "Videos": {".mp4", ".mkv", ".mov", ".avi", ".webm"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz"},
    "Code": {".py", ".js", ".html", ".css", ".json", ".java", ".c", ".cpp", ".ts", ".sh"},
    "Music": {".mp3", ".wav", ".flac", ".aac", ".m4a"},
}
DEFAULT_CATEGORY = "Other"
SEPARATOR = "=" * 50
SCRIPT_PATH = Path(__file__).resolve()

# Reverse lookup (".pdf" -> "Documents") built once for O(1) classification.
EXT_TO_CATEGORY = {ext: cat for cat, exts in EXTENSION_MAP.items() for ext in exts}


def categorize(filename):
    """Return the category folder name for *filename* (case-insensitive)."""
    return EXT_TO_CATEGORY.get(Path(filename).suffix.lower(), DEFAULT_CATEGORY)


def unique_destination(dest_dir, filename, reserved=None):
    """Return a destination path that does not clash with anything.

    If dest_dir/filename exists (or is already reserved by an earlier
    planned move in this run), a counter is appended: name_1.ext, name_2.ext...
    """
    reserved = reserved if reserved is not None else set()
    candidate = dest_dir / filename
    stem, suffix = Path(filename).stem, Path(filename).suffix
    counter = 1
    # lexists() also detects broken symlinks, which exists() would miss.
    while os.path.lexists(candidate) or candidate in reserved:
        candidate = dest_dir / f"{stem}_{counter}{suffix}"
        counter += 1
    return candidate


def organize(target, dry_run=False):
    """Organise *target*. Return a stats dict (moved/skipped/errors/by_category)."""
    stats = {"moved": 0, "skipped": 0, "errors": 0, "by_category": {}, "interrupted": False}
    reserved = set()  # destinations planned so far (matters for --dry-run)

    # Take a snapshot first: we create folders inside target while looping.
    with os.scandir(target) as it:
        entries = sorted(it, key=lambda e: e.name.lower())

    try:
        for entry in entries:
            try:
                # --- things we deliberately never move ---
                if entry.is_dir(follow_symlinks=False):
                    print(f"⚠ Skipped (folder):  {entry.name}")
                    stats["skipped"] += 1
                    continue
                if (not entry.is_file(follow_symlinks=False)
                        or entry.name.startswith(".")
                        or Path(entry.path).resolve() == SCRIPT_PATH):
                    print(f"⚠ Skipped (special): {entry.name}")
                    stats["skipped"] += 1
                    continue

                category = categorize(entry.name)
                dest_dir = Path(target) / category
                if not dry_run:
                    dest_dir.mkdir(exist_ok=True)  # create folder on demand
                dest = unique_destination(dest_dir, entry.name, reserved)
                reserved.add(dest)

                if dry_run:
                    print(f"📄 [DRY RUN] {entry.name}  ->  {category}/{dest.name}")
                else:
                    shutil.move(entry.path, str(dest))
                    print(f"✔ {entry.name}  ->  {category}/{dest.name}")
                stats["moved"] += 1
                stats["by_category"][category] = stats["by_category"].get(category, 0) + 1

            # One bad file must never stop the run.
            except PermissionError:
                print(f"❌ Permission denied: {entry.name}")
                stats["errors"] += 1
            except FileExistsError:
                print(f"❌ Destination already exists / name conflict: {entry.name}")
                stats["errors"] += 1
            except OSError as exc:  # includes shutil.Error
                print(f"❌ Could not move {entry.name}: {exc}")
                stats["errors"] += 1
    except KeyboardInterrupt:
        print("\n⚠ Interrupted by user - stopping early.")
        stats["interrupted"] = True
    return stats


def print_summary(stats, target, dry_run):
    """Print the final report (moved / skipped / errors / timestamp)."""
    verb = "Would move" if dry_run else "Moved"
    print(SEPARATOR)
    print("📊 SUMMARY" + ("  (dry run - nothing was changed)" if dry_run else ""))
    print(SEPARATOR)
    print(f"{'Directory:':<12}{target}")
    print(f"{verb + ':':<12}{stats['moved']}")
    print(f"{'Skipped:':<12}{stats['skipped']}")
    print(f"{'Errors:':<12}{stats['errors']}")
    for category, count in sorted(stats["by_category"].items()):
        print(f"   - {category:<10}{count}")
    print(f"{'Finished:':<12}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(SEPARATOR)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Sort files in a directory into category folders by extension.")
    parser.add_argument("path", help="directory to organise")
    parser.add_argument("--dry-run", action="store_true",
                        help="preview the moves without changing anything")
    return parser.parse_args(argv)


def main():
    args = parse_args()
    target = Path(args.path).expanduser().resolve()

    if not target.exists():
        print(f"❌ Path does not exist: {target}")
        sys.exit(1)
    if not target.is_dir():
        print(f"❌ Not a directory: {target}")
        sys.exit(1)

    print(SEPARATOR)
    print("🗂️  FILE ORGANIZER  -  Datheon Internship")
    print(SEPARATOR)
    print(f"Target: {target}")
    print("Mode:   " + ("DRY RUN (preview only)" if args.dry_run else "LIVE (files will be moved)"))
    print(SEPARATOR)

    try:
        stats = organize(target, args.dry_run)
    except PermissionError:
        print(f"❌ Permission denied reading directory: {target}")
        sys.exit(1)
    except OSError as exc:
        print(f"❌ Cannot read directory: {exc}")
        sys.exit(1)

    print_summary(stats, target, args.dry_run)


if __name__ == "__main__":
    main()
