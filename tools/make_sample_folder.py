"""Sample test environment generator for Smart File Organizer.

This utility creates a safe test directory populated with dummy files representing
every supported category, mixed-case extensions, files without extensions,
pre-existing duplicate collision scenarios, system files, and nested subfolders.
It contains zero delete calls to preserve file safety.
"""

from pathlib import Path
import sys
from typing import Dict, List, Tuple


def get_target_directory() -> Path:
    """Determine the destination path for the sample test folder.

    Returns:
        Path object pointing to the sample_test_folder directory.
    """
    if len(sys.argv) > 1:
        return Path(sys.argv[1]).resolve()
    # Default to placing sample_test_folder in the project root directory
    project_root = Path(__file__).resolve().parent.parent
    return project_root / "sample_test_folder"


def create_dummy_file(file_path: Path, content: str = "") -> None:
    """Create a dummy file with tiny text content without deleting existing data."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, mode="w", encoding="utf-8") as file:
        file.write(content if content else f"Dummy content for testing: {file_path.name}\n")


def build_sample_environment(target_folder: Path) -> List[Path]:
    """Populate the target folder with dummy files covering all test requirements.

    Args:
        target_folder: Path to the test directory to build.

    Returns:
        List of Path objects created.
    """
    target_folder.mkdir(parents=True, exist_ok=True)
    created_files: List[Path] = []

    # Category coverage with mixed-case and standard extensions
    sample_files: List[Tuple[str, str]] = [
        # Images (includes uppercase .JPG)
        ("vacation.JPG", "JPEG image dummy"),
        ("diagram.png", "PNG image dummy"),
        ("vector_logo.svg", "SVG vector dummy"),
        ("favicon.ico", "ICO icon dummy"),
        # Documents (includes mixed-case .Pdf)
        ("manual.Pdf", "PDF document dummy"),
        ("meeting_notes.txt", "Plain text document dummy"),
        ("project_spec.docx", "Word document dummy"),
        ("summary.odt", "OpenDocument text dummy"),
        # Videos
        ("screen_recording.mp4", "MP4 video dummy"),
        ("presentation_clip.mkv", "MKV video dummy"),
        # Audio
        ("podcast_episode.mp3", "MP3 audio dummy"),
        ("notification_sound.wav", "WAV audio dummy"),
        # Archives
        ("archive_backup.zip", "ZIP archive dummy"),
        ("distribution.tar.gz", "TAR GZ archive dummy"),
        # Code Files
        ("script.py", "# Python script dummy\nprint('hello')\n"),
        ("styles.css", "body { color: black; }"),
        ("app_config.json", '{"name": "test"}'),
        ("index.html", "<!DOCTYPE html><html><body>Test</body></html>"),
        # Spreadsheets
        ("quarterly_budget.xlsx", "Excel spreadsheet dummy"),
        ("sensor_data.csv", "timestamp,value\n2026-10-14,42\n"),
        # Presentations
        ("defense_slides.pptx", "PowerPoint presentation dummy"),
        ("keynote_deck.key", "Keynote presentation dummy"),
        # Other Files (unrecognized extension and file without extension)
        ("firmware_binary.bin", "Binary file dummy"),
        ("LICENSE_NO_EXTENSION", "File with no extension dummy"),
        # Collision scenario: Duplicate filename
        # A root report.pdf plus a pre-existing Documents/report.pdf
        ("report.pdf", "New incoming report file that should be renamed upon move"),
        # Exclusion test files (must be skipped by organizer)
        (".hidden_config", "Hidden file that should be ignored"),
        ("desktop.ini", "[.ShellClassInfo]\nIconIndex=0\n"),
        ("Thumbs.db", "Thumbnail database dummy"),
        ("~$draft_document.docx", "Temporary lock file dummy"),
        ("scratch_cache.tmp", "Temporary cache file dummy"),
    ]

    for rel_path, content in sample_files:
        path = target_folder / rel_path
        create_dummy_file(path, content)
        created_files.append(path)

    # Pre-existing category folder file to trigger duplicate rename resolution
    pre_existing_doc = target_folder / "Documents" / "report.pdf"
    create_dummy_file(pre_existing_doc, "Pre-existing report file inside Documents category folder")
    created_files.append(pre_existing_doc)

    # Subfolder with files to test include_subfolders functionality
    nested_dir = target_folder / "project_subfolder"
    nested_file_1 = nested_dir / "nested_notes.txt"
    nested_file_2 = nested_dir / "nested_photo.png"
    create_dummy_file(nested_file_1, "Notes located inside a subfolder")
    create_dummy_file(nested_file_2, "Photo located inside a subfolder")
    created_files.append(nested_file_1)
    created_files.append(nested_file_2)

    return created_files


def main() -> None:
    """Build the test environment and display verification information."""
    target_folder = get_target_directory()
    created = build_sample_environment(target_folder)

    print("=" * 60)
    print("Smart File Organizer - Test Environment Generator")
    print("=" * 60)
    print(f"Target Directory: {target_folder}")
    print(f"Total Test Files Populated: {len(created)}")
    print("\nIncluded Test Cases:")
    print("  - All 9 file categories represented")
    print("  - Uppercase and mixed-case extensions (.JPG, .Pdf)")
    print("  - File with no extension (LICENSE_NO_EXTENSION)")
    print("  - Pre-existing duplicate (Documents/report.pdf vs root report.pdf)")
    print("  - Excluded files (.hidden_config, desktop.ini, Thumbs.db, ~$draft, .tmp)")
    print("  - Nested subfolder (project_subfolder/)")
    print("\nInstructions:")
    print("  1. Launch Smart File Organizer: python main.py")
    print(f"  2. In the GUI, select folder: {target_folder}")
    print("  3. Click 'Preview' to inspect planned movements")
    print("  4. Verify that report.pdf is planned as 'report (1).pdf'")
    print("  5. Verify that hidden/system/temp files are excluded")
    print("  6. Click 'Organize Files' to complete the safe test run")
    print("=" * 60)


if __name__ == "__main__":
    main()
