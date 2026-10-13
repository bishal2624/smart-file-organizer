"""Activity logging and JSON summary reporting module for Smart File Organizer.

This module handles persistent auditing of all file management actions into a
structured CSV log file and serializes organize-session reports into JSON files.
All file access is guarded against concurrency issues and permission errors.
"""

import csv
from datetime import datetime
import json
from pathlib import Path
import threading
from typing import Any, Dict, List, Optional

from config import (
    ACTIVITY_LOG_FILENAME,
    LOGS_DIR,
    SUMMARY_REPORT_PREFIX,
)

# Standard CSV header columns for the activity log
CSV_COLUMNS: List[str] = [
    "timestamp",
    "action",
    "filename",
    "source",
    "destination",
    "status",
    "message",
]

# Thread lock to guarantee safe sequential writes to the shared CSV log
_LOG_LOCK: threading.Lock = threading.Lock()


def get_logs_dir() -> Path:
    """Return the absolute path to the logs directory, creating it if needed."""
    try:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
    except OSError:
        # Fall back to current working directory if project root is not writable
        fallback = Path.cwd() / "logs"
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback
    return LOGS_DIR


def get_activity_log_path() -> Path:
    """Return the path to the active activity_log.csv file."""
    return get_logs_dir() / ACTIVITY_LOG_FILENAME


def initialize_log_file() -> None:
    """Ensure the activity_log.csv file exists and contains the header row."""
    log_path = get_activity_log_path()
    with _LOG_LOCK:
        if not log_path.exists() or log_path.stat().st_size == 0:
            try:
                with open(log_path, mode="w", newline="", encoding="utf-8") as file:
                    writer = csv.writer(file)
                    writer.writerow(CSV_COLUMNS)
            except OSError:
                pass


def log_event(
    action: str,
    filename: str = "",
    source: str = "",
    destination: str = "",
    status: str = "INFO",
    message: str = "",
) -> bool:
    """Append a single audit record to the CSV activity log.

    Args:
        action: Type of action performed (e.g., SCAN, MOVE, SKIP, ERROR).
        filename: Name of the file being processed.
        source: Full original path of the file.
        destination: Full target path of the file.
        status: Outcome status (e.g., SUCCESS, SKIPPED, FAILED, INFO).
        message: Plain-language explanation or error detail.

    Returns:
        True if the event was successfully written, False otherwise.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_path = get_activity_log_path()
    row = [timestamp, action, filename, source, destination, status, message]

    with _LOG_LOCK:
        try:
            write_header = not log_path.exists() or log_path.stat().st_size == 0
            with open(log_path, mode="a", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                if write_header:
                    writer.writerow(CSV_COLUMNS)
                writer.writerow(row)
            return True
        except (OSError, PermissionError):
            return False


def read_log() -> List[Dict[str, str]]:
    """Read all entries from the activity log, returning them newest first.

    Returns:
        A list of row dictionaries mapping column headers to string values.
    """
    log_path = get_activity_log_path()
    if not log_path.exists():
        return []

    entries: List[Dict[str, str]] = []
    with _LOG_LOCK:
        try:
            with open(log_path, mode="r", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Clean any missing or malformed keys
                    cleaned = {col: row.get(col, "") for col in CSV_COLUMNS}
                    entries.append(cleaned)
        except (OSError, PermissionError):
            return []

    # Return newest entries at the beginning for immediate display in UI
    entries.reverse()
    return entries


def clear_log() -> bool:
    """Clear all records from the activity log by resetting to header row only.

    Returns:
        True if the file was reset successfully, False otherwise.
    """
    log_path = get_activity_log_path()
    with _LOG_LOCK:
        try:
            with open(log_path, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(CSV_COLUMNS)
            return True
        except (OSError, PermissionError):
            return False


def save_report(results: Dict[str, Any]) -> Optional[Path]:
    """Serialize the results of an organize operation to a timestamped JSON file.

    Args:
        results: Dictionary containing execution statistics and outcome details.

    Returns:
        Path to the generated JSON report, or None if saving failed.
    """
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"{SUMMARY_REPORT_PREFIX}{timestamp_str}.json"
    report_path = get_logs_dir() / report_filename

    try:
        with open(report_path, mode="w", encoding="utf-8") as file:
            json.dump(results, file, indent=2, default=str)
        return report_path
    except (OSError, TypeError):
        return None
