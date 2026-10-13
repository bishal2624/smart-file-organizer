"""Configuration module for Smart File Organizer.

This module defines all category mappings, extension sets, UI color palettes,
typography rules, system-critical folder constraints, and exclusion lists.
Centralizing these values ensures consistent behavior across the application
and allows adjustments in a single location.
"""

from pathlib import Path
import sys
from typing import Dict, List, Set, Tuple

# Application metadata
APP_TITLE: str = "Smart File Organizer"
APP_SUBTITLE: str = "An Automated Desktop File Management System"
APP_VERSION: str = "1.0.0"

# Base directory paths
# Resolve paths relative to this config file so execution does not depend on current working directory
BASE_DIR: Path = Path(__file__).resolve().parent
LOGS_DIR: Path = BASE_DIR / "logs"
ACTIVITY_LOG_FILENAME: str = "activity_log.csv"
SUMMARY_REPORT_PREFIX: str = "report_"

# Window layout dimensions
DEFAULT_WINDOW_WIDTH: int = 1100
DEFAULT_WINDOW_HEIGHT: int = 700
MIN_WINDOW_WIDTH: int = 900
MIN_WINDOW_HEIGHT: int = 600
SIDEBAR_WIDTH: int = 200

# Padding standards (in pixels)
PAD_SMALL: int = 8
PAD_MEDIUM: int = 12
PAD_LARGE: int = 16

# Category names and their associated lowercase extensions (with leading dot)
# Other Files is handled dynamically for any extension not listed below
CATEGORY_EXTENSIONS: Dict[str, Tuple[str, ...]] = {
    "Images": (
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".webp",
        ".svg",
        ".tiff",
        ".ico",
        ".heic",
    ),
    "Documents": (
        ".pdf",
        ".doc",
        ".docx",
        ".txt",
        ".rtf",
        ".odt",
        ".md",
        ".epub",
    ),
    "Videos": (
        ".mp4",
        ".mkv",
        ".avi",
        ".mov",
        ".wmv",
        ".flv",
        ".webm",
        ".m4v",
    ),
    "Audio": (
        ".mp3",
        ".wav",
        ".flac",
        ".aac",
        ".ogg",
        ".m4a",
        ".wma",
    ),
    "Archives": (
        ".zip",
        ".rar",
        ".7z",
        ".tar",
        ".gz",
        ".bz2",
        ".xz",
    ),
    "Code Files": (
        ".py",
        ".js",
        ".ts",
        ".html",
        ".css",
        ".java",
        ".c",
        ".cpp",
        ".h",
        ".cs",
        ".php",
        ".rb",
        ".go",
        ".rs",
        ".sql",
        ".json",
        ".xml",
        ".yaml",
        ".yml",
        ".sh",
        ".bat",
        ".ipynb",
    ),
    "Spreadsheets": (
        ".xls",
        ".xlsx",
        ".csv",
        ".ods",
        ".tsv",
    ),
    "Presentations": (
        ".ppt",
        ".pptx",
        ".odp",
        ".key",
    ),
}

DEFAULT_CATEGORY: str = "Other Files"

# Ordered list of all valid destination categories
ALL_CATEGORIES: List[str] = list(CATEGORY_EXTENSIONS.keys()) + [DEFAULT_CATEGORY]

# Flattened dictionary for O(1) category lookup: {".pdf": "Documents", ...}
EXTENSION_MAP: Dict[str, str] = {
    ext.lower(): category
    for category, extensions in CATEGORY_EXTENSIONS.items()
    for ext in extensions
}

# Exclusion rules
# Exact filenames to skip during scanning (case-insensitive check)
EXCLUDED_FILENAMES: Set[str] = {
    "desktop.ini",
    "thumbs.db",
    ACTIVITY_LOG_FILENAME,
}

# Prefix and suffix patterns for files that should never be moved
EXCLUDED_PREFIXES: Tuple[str, ...] = (".", "~$")
EXCLUDED_SUFFIXES: Tuple[str, ...] = (".tmp",)

# Source code files of this project that must never be moved if the user
# selects the application root folder itself
APP_SOURCE_FILES: Set[str] = {
    "main.py",
    "gui.py",
    "organizer.py",
    "logger.py",
    "config.py",
    "requirements.txt",
    "readme.md",
    ".gitignore",
}

# Color palette: Strict light theme
# Strictly neutral backgrounds, dark slate sidebar, blue accent, no purple
COLOR_PRIMARY_BG: str = "#F9FAFB"        # Light neutral page background
COLOR_SURFACE: str = "#FFFFFF"           # Clean white card surface
COLOR_SIDEBAR_BG: str = "#1F2937"        # Dark slate sidebar background
COLOR_SIDEBAR_ACTIVE: str = "#374151"    # Darker slate for selected navigation button
COLOR_SIDEBAR_TEXT: str = "#F9FAFB"      # High contrast light text for sidebar
COLOR_SIDEBAR_MUTED: str = "#9CA3AF"     # Subdued text for sidebar headers
COLOR_ACCENT: str = "#2563EB"            # Primary action blue
COLOR_ACCENT_HOVER: str = "#1D4ED8"      # Darker blue on hover
COLOR_ACCENT_TEXT: str = "#FFFFFF"       # White text on accent buttons
COLOR_TEXT_PRIMARY: str = "#111827"      # High contrast dark text for content
COLOR_TEXT_SECONDARY: str = "#4B5563"    # Medium contrast text for secondary labels
COLOR_BORDER: str = "#E5E7EB"            # Soft border line for cards and dividers
COLOR_TREEVIEW_ALT: str = "#F3F4F6"      # Alternating row background for tables
COLOR_SUCCESS: str = "#059669"           # Forest green for successful operations
COLOR_WARNING: str = "#D97706"           # Amber for warnings and skipped items
COLOR_WARNING_BG: str = "#FEF3C7"        # Soft amber highlight background for renamed duplicates
COLOR_WARNING_TEXT: str = "#92400E"      # High contrast amber text for renamed duplicates
COLOR_DANGER: str = "#DC2626"            # Red for errors and failed moves

# Typography specifications
# Segoe UI is default on Windows: Helvetica and Arial serve as cross-platform fallbacks
FONT_FAMILY: str = "Segoe UI" if sys.platform.startswith("win") else "Helvetica"
FONT_TITLE: Tuple[str, int, str] = (FONT_FAMILY, 18, "bold")
FONT_HEADING: Tuple[str, int, str] = (FONT_FAMILY, 12, "bold")
FONT_BODY: Tuple[str, int, str] = (FONT_FAMILY, 10, "normal")
FONT_BODY_BOLD: Tuple[str, int, str] = (FONT_FAMILY, 10, "bold")
FONT_SMALL: Tuple[str, int, str] = (FONT_FAMILY, 9, "normal")
FONT_MONO: Tuple[str, int, str] = ("Consolas" if sys.platform.startswith("win") else "Courier", 9, "normal")
