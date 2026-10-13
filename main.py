"""Application entry point for Smart File Organizer.

This module initializes the application runtime, configures global error logging,
verifies standard library dependencies, sets up the Tkinter main window, and
starts the event loop.
"""

import sys
import tkinter as tk

from config import APP_TITLE
from gui import AppGUI, handle_uncaught_exception
from logger import initialize_log_file, log_event


def main() -> None:
    """Initialize resources and launch the Smart File Organizer GUI application."""
    # Ensure logs folder and CSV activity log header exist before GUI loads
    initialize_log_file()
    log_event("APP_START", "", "", "", "INFO", "Smart File Organizer started.")

    # Initialize Tkinter root window
    root = tk.Tk()
    root.title(APP_TITLE)

    # Attach global exception handler so unhandled callback exceptions are captured
    root.report_callback_exception = handle_uncaught_exception

    # Construct the primary application interface
    AppGUI(root)

    # Begin the main Tkinter event loop
    try:
        root.mainloop()
    finally:
        log_event("APP_EXIT", "", "", "", "INFO", "Smart File Organizer closed cleanly.")


if __name__ == "__main__":
    main()
