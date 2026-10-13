"""Graphical User Interface module for Smart File Organizer.

This module implements the complete desktop interface using Tkinter and ttk.
The layout features a fixed-width dark sidebar and a main multi-page content area.
Background threads handle scanning and execution without freezing the interface.
"""

from datetime import datetime
import os
from pathlib import Path
import queue
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Any, Dict, List, Optional, Tuple

from config import (
    ALL_CATEGORIES,
    APP_SUBTITLE,
    APP_TITLE,
    APP_VERSION,
    COLOR_ACCENT,
    COLOR_ACCENT_HOVER,
    COLOR_ACCENT_TEXT,
    COLOR_BORDER,
    COLOR_DANGER,
    COLOR_PRIMARY_BG,
    COLOR_SIDEBAR_ACTIVE,
    COLOR_SIDEBAR_BG,
    COLOR_SIDEBAR_MUTED,
    COLOR_SIDEBAR_TEXT,
    COLOR_SUCCESS,
    COLOR_SURFACE,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_TREEVIEW_ALT,
    COLOR_WARNING,
    COLOR_WARNING_BG,
    COLOR_WARNING_TEXT,
    DEFAULT_WINDOW_HEIGHT,
    DEFAULT_WINDOW_WIDTH,
    FONT_BODY,
    FONT_BODY_BOLD,
    FONT_FAMILY,
    FONT_HEADING,
    FONT_MONO,
    FONT_SMALL,
    FONT_TITLE,
    LOGS_DIR,
    MIN_WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH,
    PAD_LARGE,
    PAD_MEDIUM,
    PAD_SMALL,
    SIDEBAR_WIDTH,
)
from logger import clear_log, log_event, read_log
from organizer import (
    build_plan,
    execute_plan,
    scan_folder,
    validate_folder,
)


class SummaryDialog(tk.Toplevel):
    """Modal dialog displaying the comprehensive execution report after organizing."""

    def __init__(self, parent: tk.Tk, results: Dict[str, Any]) -> None:
        super().__init__(parent)
        self.title("Run Summary - Smart File Organizer")
        self.results = results
        self.transient(parent)
        self.grab_set()

        self.geometry("640x540")
        self.minsize(580, 480)
        self.configure(bg=COLOR_PRIMARY_BG)
        self._center_window(parent)
        self._create_widgets()

    def _center_window(self, parent: tk.Tk) -> None:
        self.update_idletasks()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        w = 640
        h = 540
        x = px + max(0, (pw - w) // 2)
        y = py + max(0, (ph - h) // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _create_widgets(self) -> None:
        main_frame = tk.Frame(self, bg=COLOR_PRIMARY_BG, padx=PAD_LARGE, pady=PAD_LARGE)
        main_frame.pack(fill=tk.BOTH, expand=True)

        header_label = tk.Label(
            main_frame,
            text="Organization Summary",
            font=FONT_HEADING,
            bg=COLOR_PRIMARY_BG,
            fg=COLOR_TEXT_PRIMARY,
        )
        header_label.pack(anchor="w", pady=(0, PAD_MEDIUM))

        # Metrics card
        metrics_card = tk.Frame(
            main_frame,
            bg=COLOR_SURFACE,
            highlightthickness=1,
            highlightbackground=COLOR_BORDER,
            padx=PAD_MEDIUM,
            pady=PAD_MEDIUM,
        )
        metrics_card.pack(fill=tk.X, pady=(0, PAD_MEDIUM))

        folder_text = f"Folder: {self.results.get('folder', '')}"
        time_text = f"Duration: {self.results.get('start_time', '')} to {self.results.get('end_time', '')}"
        counts_text = (
            f"Planned: {self.results.get('total_files', 0)}  |  "
            f"Moved: {self.results.get('moved', 0)}  |  "
            f"Skipped: {self.results.get('skipped', 0)}  |  "
            f"Failed: {self.results.get('failed', 0)}"
        )

        tk.Label(metrics_card, text=folder_text, font=FONT_BODY, bg=COLOR_SURFACE, fg=COLOR_TEXT_PRIMARY, anchor="w").pack(fill=tk.X)
        tk.Label(metrics_card, text=time_text, font=FONT_SMALL, bg=COLOR_SURFACE, fg=COLOR_TEXT_SECONDARY, anchor="w", pady=4).pack(fill=tk.X)
        tk.Label(metrics_card, text=counts_text, font=FONT_BODY_BOLD, bg=COLOR_SURFACE, fg=COLOR_ACCENT, anchor="w").pack(fill=tk.X)

        # Per-category summary list
        cat_frame = tk.Frame(
            main_frame,
            bg=COLOR_SURFACE,
            highlightthickness=1,
            highlightbackground=COLOR_BORDER,
            padx=PAD_MEDIUM,
            pady=PAD_SMALL,
        )
        cat_frame.pack(fill=tk.X, pady=(0, PAD_MEDIUM))

        tk.Label(cat_frame, text="Files Moved Per Category:", font=FONT_BODY_BOLD, bg=COLOR_SURFACE, fg=COLOR_TEXT_PRIMARY).pack(anchor="w", pady=(0, 4))
        cat_counts: Dict[str, int] = self.results.get("category_counts", {})
        cat_items = [f"{cat}: {count}" for cat, count in cat_counts.items() if count > 0]
        cat_display = ", ".join(cat_items) if cat_items else "No files moved."
        tk.Label(cat_frame, text=cat_display, font=FONT_BODY, bg=COLOR_SURFACE, fg=COLOR_TEXT_SECONDARY, wraplength=580, justify="left").pack(anchor="w")

        # Failures section
        failures: List[Dict[str, str]] = self.results.get("failures", [])
        fail_title = f"Failures Encountered ({len(failures)}):"
        tk.Label(main_frame, text=fail_title, font=FONT_BODY_BOLD, bg=COLOR_PRIMARY_BG, fg=COLOR_TEXT_PRIMARY).pack(anchor="w", pady=(0, 4))

        list_container = tk.Frame(main_frame, bg=COLOR_SURFACE, highlightthickness=1, highlightbackground=COLOR_BORDER)
        list_container.pack(fill=tk.BOTH, expand=True, pady=(0, PAD_MEDIUM))

        scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL)
        fail_listbox = tk.Listbox(
            list_container,
            yscrollcommand=scrollbar.set,
            bg=COLOR_SURFACE,
            fg=COLOR_DANGER if failures else COLOR_TEXT_SECONDARY,
            font=FONT_SMALL,
            borderwidth=0,
            highlightthickness=0,
        )
        scrollbar.config(command=fail_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        fail_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        if failures:
            for item in failures:
                fail_listbox.insert(tk.END, f"{item.get('filename')}: {item.get('reason')}")
        else:
            fail_listbox.insert(tk.END, "None. All eligible files were organized without errors.")

        # Bottom actions
        button_row = tk.Frame(main_frame, bg=COLOR_PRIMARY_BG)
        button_row.pack(fill=tk.X)

        open_btn = ttk.Button(button_row, text="Open Folder", command=self._open_target_folder)
        open_btn.pack(side=tk.LEFT)

        close_btn = ttk.Button(button_row, text="Close", command=self.destroy)
        close_btn.pack(side=tk.RIGHT)

    def _open_target_folder(self) -> None:
        target = self.results.get("folder", "")
        if target and os.path.exists(target):
            open_folder_in_explorer(Path(target))


def open_folder_in_explorer(folder_path: Path) -> None:
    """Open a directory in the default operating system file manager."""
    try:
        resolved = folder_path.resolve()
        if sys.platform.startswith("win"):
            os.startfile(str(resolved))
        elif sys.platform.startswith("darwin"):
            subprocess.Popen(["open", str(resolved)])
        else:
            subprocess.Popen(["xdg-open", str(resolved)])
    except Exception as err:
        messagebox.showwarning(
            "Open Folder Warning",
            f"Could not automatically open folder: {str(err)}\nPath: {folder_path}",
        )


class AppGUI:
    """Primary GUI Application Controller for Smart File Organizer."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(f"{DEFAULT_WINDOW_WIDTH}x{DEFAULT_WINDOW_HEIGHT}")
        self.root.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        self.root.configure(bg=COLOR_PRIMARY_BG)

        # State variables
        self.selected_folder: Optional[Path] = None
        self.scanned_files: List[Path] = []
        self.current_plan: List[Dict[str, Any]] = []
        self.include_subfolders_var = tk.BooleanVar(value=False)
        self.active_page: str = "dashboard"

        # Threading and background queue
        self.work_queue: queue.Queue = queue.Queue()
        self.cancel_flag = threading.Event()
        self.is_running: bool = False

        # Set up styles, layout, and global error handling
        self._setup_styles()
        self._center_window()
        self._build_main_layout()
        self._bind_events()
        self._poll_work_queue()

    def _center_window(self) -> None:
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = max(0, (sw - DEFAULT_WINDOW_WIDTH) // 2)
        y = max(0, (sh - DEFAULT_WINDOW_HEIGHT) // 2)
        self.root.geometry(f"{DEFAULT_WINDOW_WIDTH}x{DEFAULT_WINDOW_HEIGHT}+{x}+{y}")

    def _setup_styles(self) -> None:
        self.style = ttk.Style(self.root)
        # Use clam theme for rectangular, predictable components without gradients
        if "clam" in self.style.theme_names():
            self.style.theme_use("clam")

        # Configure base ttk elements
        self.style.configure(".", background=COLOR_PRIMARY_BG, font=FONT_BODY)
        self.style.configure("TFrame", background=COLOR_PRIMARY_BG)
        self.style.configure("TLabel", background=COLOR_PRIMARY_BG, foreground=COLOR_TEXT_PRIMARY, font=FONT_BODY)

        # Primary and regular buttons
        self.style.configure(
            "TButton",
            font=FONT_BODY_BOLD,
            background=COLOR_SURFACE,
            foreground=COLOR_TEXT_PRIMARY,
            borderwidth=1,
            relief="solid",
            padding=(PAD_MEDIUM, 6),
        )
        self.style.map(
            "TButton",
            background=[("pressed", COLOR_TREEVIEW_ALT), ("active", COLOR_TREEVIEW_ALT)],
            foreground=[("disabled", COLOR_TEXT_SECONDARY)],
        )

        self.style.configure(
            "Accent.TButton",
            font=FONT_BODY_BOLD,
            background=COLOR_ACCENT,
            foreground=COLOR_ACCENT_TEXT,
            borderwidth=0,
            padding=(PAD_MEDIUM, 6),
        )
        self.style.map(
            "Accent.TButton",
            background=[("pressed", COLOR_ACCENT_HOVER), ("active", COLOR_ACCENT_HOVER), ("disabled", COLOR_BORDER)],
            foreground=[("disabled", COLOR_TEXT_SECONDARY)],
        )

        # Danger button for cancel
        self.style.configure(
            "Danger.TButton",
            font=FONT_BODY_BOLD,
            background=COLOR_DANGER,
            foreground=COLOR_ACCENT_TEXT,
            borderwidth=0,
            padding=(PAD_MEDIUM, 6),
        )
        self.style.map(
            "Danger.TButton",
            background=[("disabled", COLOR_BORDER)],
            foreground=[("disabled", COLOR_TEXT_SECONDARY)],
        )

        # Progress bar configuration
        self.style.configure(
            "Horizontal.TProgressbar",
            background=COLOR_ACCENT,
            troughcolor=COLOR_BORDER,
            borderwidth=0,
            thickness=10,
        )

        # Treeview styling
        self.style.configure(
            "Treeview",
            background=COLOR_SURFACE,
            foreground=COLOR_TEXT_PRIMARY,
            fieldbackground=COLOR_SURFACE,
            rowheight=26,
            font=FONT_BODY,
            borderwidth=0,
        )
        self.style.configure(
            "Treeview.Heading",
            background=COLOR_TREEVIEW_ALT,
            foreground=COLOR_TEXT_PRIMARY,
            font=FONT_BODY_BOLD,
            relief="flat",
            padding=(6, 4),
        )
        self.style.map("Treeview", background=[("selected", COLOR_ACCENT)], foreground=[("selected", COLOR_ACCENT_TEXT)])

    def _build_main_layout(self) -> None:
        # Sidebar container
        self.sidebar_frame = tk.Frame(self.root, bg=COLOR_SIDEBAR_BG, width=SIDEBAR_WIDTH)
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar_frame.pack_propagate(False)

        # Content container
        self.content_container = tk.Frame(self.root, bg=COLOR_PRIMARY_BG)
        self.content_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self._build_sidebar()
        self._build_pages()
        self.show_page("dashboard")

    def _build_sidebar(self) -> None:
        # App brand header in sidebar
        brand_frame = tk.Frame(self.sidebar_frame, bg=COLOR_SIDEBAR_BG, padx=PAD_MEDIUM, pady=PAD_LARGE)
        brand_frame.pack(fill=tk.X)

        title_lbl = tk.Label(
            brand_frame,
            text=APP_TITLE,
            font=FONT_HEADING,
            bg=COLOR_SIDEBAR_BG,
            fg=COLOR_SIDEBAR_TEXT,
            wraplength=SIDEBAR_WIDTH - 24,
            justify="left",
        )
        title_lbl.pack(anchor="w")

        version_lbl = tk.Label(
            brand_frame,
            text=f"v{APP_VERSION} (Offline)",
            font=FONT_SMALL,
            bg=COLOR_SIDEBAR_BG,
            fg=COLOR_SIDEBAR_MUTED,
        )
        version_lbl.pack(anchor="w", pady=(2, 0))

        # Nav items list
        self.nav_buttons: Dict[str, tk.Button] = {}
        nav_items = [
            ("dashboard", "Dashboard"),
            ("preview", "Preview"),
            ("activity_log", "Activity Log"),
            ("about", "About"),
        ]

        nav_frame = tk.Frame(self.sidebar_frame, bg=COLOR_SIDEBAR_BG, pady=PAD_SMALL)
        nav_frame.pack(fill=tk.X)

        for page_id, label_text in nav_items:
            btn = tk.Button(
                nav_frame,
                text=label_text,
                font=FONT_BODY_BOLD,
                bg=COLOR_SIDEBAR_BG,
                fg=COLOR_SIDEBAR_TEXT,
                activebackground=COLOR_SIDEBAR_ACTIVE,
                activeforeground=COLOR_SIDEBAR_TEXT,
                bd=0,
                padx=PAD_LARGE,
                pady=10,
                anchor="w",
                cursor="hand2",
                command=lambda pid=page_id: self.show_page(pid),
            )
            btn.pack(fill=tk.X)
            self.nav_buttons[page_id] = btn

    def _build_pages(self) -> None:
        self.pages: Dict[str, tk.Frame] = {}

        # 1. Dashboard Page
        self.pages["dashboard"] = self._create_dashboard_page()
        # 2. Preview Page
        self.pages["preview"] = self._create_preview_page()
        # 3. Activity Log Page
        self.pages["activity_log"] = self._create_activity_log_page()
        # 4. About Page
        self.pages["about"] = self._create_about_page()

    def show_page(self, page_id: str) -> None:
        """Switch visible page and update sidebar highlight."""
        self.active_page = page_id
        for pid, frame in self.pages.items():
            if pid == page_id:
                frame.pack(fill=tk.BOTH, expand=True)
            else:
                frame.pack_forget()

        for pid, btn in self.nav_buttons.items():
            if pid == page_id:
                btn.configure(bg=COLOR_SIDEBAR_ACTIVE, fg=COLOR_SIDEBAR_TEXT)
            else:
                btn.configure(bg=COLOR_SIDEBAR_BG, fg=COLOR_SIDEBAR_TEXT)

        if page_id == "activity_log":
            self.refresh_log_table()
        elif page_id == "preview":
            self.refresh_preview_table()

    # ---------------------------------------------------------
    # Dashboard Page Construction
    # ---------------------------------------------------------
    def _create_dashboard_page(self) -> tk.Frame:
        page = tk.Frame(self.content_container, bg=COLOR_PRIMARY_BG, padx=PAD_LARGE, pady=PAD_LARGE)

        # Header Title
        tk.Label(page, text="Dashboard", font=FONT_TITLE, bg=COLOR_PRIMARY_BG, fg=COLOR_TEXT_PRIMARY).pack(anchor="w", pady=(0, PAD_MEDIUM))

        # Folder Picker Card
        picker_card = tk.Frame(page, bg=COLOR_SURFACE, highlightthickness=1, highlightbackground=COLOR_BORDER, padx=PAD_MEDIUM, pady=PAD_MEDIUM)
        picker_card.pack(fill=tk.X, pady=(0, PAD_MEDIUM))

        picker_top = tk.Frame(picker_card, bg=COLOR_SURFACE)
        picker_top.pack(fill=tk.X)

        self.browse_btn = ttk.Button(picker_top, text="Browse Folder", command=self.on_browse_folder)
        self.browse_btn.pack(side=tk.LEFT, padx=(0, PAD_SMALL))

        self.path_entry_var = tk.StringVar(value="Select a folder to begin")
        self.path_entry = ttk.Entry(picker_top, textvariable=self.path_entry_var, state="readonly", font=FONT_BODY)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, PAD_SMALL))

        self.refresh_btn = ttk.Button(picker_top, text="Refresh", command=self.on_refresh_scan, state="disabled")
        self.refresh_btn.pack(side=tk.RIGHT)

        # Include subfolders checkbox with plain description
        subfolder_row = tk.Frame(picker_card, bg=COLOR_SURFACE, pady=PAD_SMALL)
        subfolder_row.pack(fill=tk.X)

        self.subfolder_cb = ttk.Checkbutton(
            subfolder_row,
            text="Include subfolders",
            variable=self.include_subfolders_var,
            command=self.on_subfolder_toggle,
        )
        self.subfolder_cb.pack(side=tk.LEFT)

        subfolder_desc = tk.Label(
            subfolder_row,
            text="(Scans nested folders, never descends into category folders)",
            font=FONT_SMALL,
            bg=COLOR_SURFACE,
            fg=COLOR_TEXT_SECONDARY,
        )
        subfolder_desc.pack(side=tk.LEFT, padx=(PAD_SMALL, 0))

        # Statistics Cards (Total, Organized, Skipped, Failed)
        stats_frame = tk.Frame(page, bg=COLOR_PRIMARY_BG)
        stats_frame.pack(fill=tk.X, pady=(0, PAD_MEDIUM))

        self.stat_cards: Dict[str, Tuple[tk.Label, tk.Label]] = {}
        stat_defs = [
            ("total", "Total Files", "0"),
            ("moved", "Organized", "0"),
            ("skipped", "Skipped", "0"),
            ("failed", "Failed", "0"),
        ]

        for idx, (stat_key, title, init_val) in enumerate(stat_defs):
            card = tk.Frame(stats_frame, bg=COLOR_SURFACE, highlightthickness=1, highlightbackground=COLOR_BORDER, padx=PAD_MEDIUM, pady=PAD_SMALL)
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0 if idx == 0 else PAD_SMALL, 0))

            t_lbl = tk.Label(card, text=title, font=FONT_SMALL, bg=COLOR_SURFACE, fg=COLOR_TEXT_SECONDARY)
            t_lbl.pack(anchor="w")

            v_lbl = tk.Label(card, text=init_val, font=FONT_HEADING, bg=COLOR_SURFACE, fg=COLOR_TEXT_PRIMARY)
            v_lbl.pack(anchor="w", pady=(2, 0))

            self.stat_cards[stat_key] = (t_lbl, v_lbl)

        # Category Counts Card
        cat_section = tk.Frame(page, bg=COLOR_SURFACE, highlightthickness=1, highlightbackground=COLOR_BORDER, padx=PAD_MEDIUM, pady=PAD_MEDIUM)
        cat_section.pack(fill=tk.BOTH, expand=True, pady=(0, PAD_MEDIUM))

        tk.Label(cat_section, text="Detected Categories (Current Scan):", font=FONT_BODY_BOLD, bg=COLOR_SURFACE, fg=COLOR_TEXT_PRIMARY).pack(anchor="w", pady=(0, PAD_SMALL))

        self.category_count_labels: Dict[str, tk.Label] = {}
        cat_grid = tk.Frame(cat_section, bg=COLOR_SURFACE)
        cat_grid.pack(fill=tk.BOTH, expand=True)

        for i, category in enumerate(ALL_CATEGORIES):
            col = i % 3
            row = i // 3
            item_box = tk.Frame(cat_grid, bg=COLOR_TREEVIEW_ALT, padx=PAD_SMALL, pady=6)
            item_box.grid(row=row, column=col, sticky="nsew", padx=4, pady=4)
            cat_grid.grid_columnconfigure(col, weight=1)

            c_name = tk.Label(item_box, text=category, font=FONT_BODY, bg=COLOR_TREEVIEW_ALT, fg=COLOR_TEXT_PRIMARY)
            c_name.pack(side=tk.LEFT)

            c_val = tk.Label(item_box, text="0", font=FONT_BODY_BOLD, bg=COLOR_TREEVIEW_ALT, fg=COLOR_ACCENT)
            c_val.pack(side=tk.RIGHT)
            self.category_count_labels[category] = c_val

        # Actions Row: Preview, Organize Files, Cancel
        action_row = tk.Frame(page, bg=COLOR_PRIMARY_BG)
        action_row.pack(fill=tk.X, pady=(0, PAD_MEDIUM))

        self.preview_btn = ttk.Button(action_row, text="Preview", command=self.on_click_preview, state="disabled")
        self.preview_btn.pack(side=tk.LEFT, padx=(0, PAD_SMALL))

        self.organize_btn = ttk.Button(action_row, text="Organize Files", style="Accent.TButton", command=self.on_click_organize, state="disabled")
        self.organize_btn.pack(side=tk.LEFT, padx=(0, PAD_SMALL))

        self.cancel_btn = ttk.Button(action_row, text="Cancel", style="Danger.TButton", command=self.on_click_cancel, state="disabled")
        self.cancel_btn.pack(side=tk.LEFT)

        # Progress and status footer
        footer_frame = tk.Frame(page, bg=COLOR_PRIMARY_BG)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.progressbar = ttk.Progressbar(footer_frame, mode="determinate", style="Horizontal.TProgressbar")
        self.progressbar.pack(fill=tk.X, pady=(0, 4))

        self.status_label = tk.Label(footer_frame, text="Ready", font=FONT_SMALL, bg=COLOR_PRIMARY_BG, fg=COLOR_TEXT_SECONDARY, anchor="w")
        self.status_label.pack(fill=tk.X)

        return page

    # ---------------------------------------------------------
    # Preview Page Construction
    # ---------------------------------------------------------
    def _create_preview_page(self) -> tk.Frame:
        page = tk.Frame(self.content_container, bg=COLOR_PRIMARY_BG, padx=PAD_LARGE, pady=PAD_LARGE)

        top_row = tk.Frame(page, bg=COLOR_PRIMARY_BG)
        top_row.pack(fill=tk.X, pady=(0, PAD_SMALL))

        tk.Label(top_row, text="Planned File Operations", font=FONT_TITLE, bg=COLOR_PRIMARY_BG, fg=COLOR_TEXT_PRIMARY).pack(side=tk.LEFT)

        self.preview_organize_now_btn = ttk.Button(
            top_row,
            text="Organize Now",
            style="Accent.TButton",
            command=self.on_click_organize,
            state="disabled",
        )
        self.preview_organize_now_btn.pack(side=tk.RIGHT)

        self.preview_summary_label = tk.Label(
            page,
            text="Select a folder to generate an execution preview.",
            font=FONT_BODY,
            bg=COLOR_PRIMARY_BG,
            fg=COLOR_TEXT_SECONDARY,
        )
        self.preview_summary_label.pack(anchor="w", pady=(0, PAD_SMALL))

        # Preview Treeview Container
        tree_container = tk.Frame(page, bg=COLOR_SURFACE, highlightthickness=1, highlightbackground=COLOR_BORDER)
        tree_container.pack(fill=tk.BOTH, expand=True)

        columns = ("filename", "extension", "category", "destination")
        self.preview_tree = ttk.Treeview(tree_container, columns=columns, show="headings", selectmode="browse")

        self.preview_tree.heading("filename", text="Filename", command=lambda: self._sort_treeview(self.preview_tree, "filename", False))
        self.preview_tree.heading("extension", text="Extension", command=lambda: self._sort_treeview(self.preview_tree, "extension", False))
        self.preview_tree.heading("category", text="Category", command=lambda: self._sort_treeview(self.preview_tree, "category", False))
        self.preview_tree.heading("destination", text="Destination Path", command=lambda: self._sort_treeview(self.preview_tree, "destination", False))

        self.preview_tree.column("filename", width=220, minwidth=140)
        self.preview_tree.column("extension", width=90, minwidth=70)
        self.preview_tree.column("category", width=120, minwidth=100)
        self.preview_tree.column("destination", width=420, minwidth=250)

        # Alternating row tag styles
        self.preview_tree.tag_configure("evenrow", background=COLOR_SURFACE)
        self.preview_tree.tag_configure("oddrow", background=COLOR_TREEVIEW_ALT)
        self.preview_tree.tag_configure("renamed", background=COLOR_WARNING_BG, foreground=COLOR_WARNING_TEXT)

        vsb = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.preview_tree.yview)
        hsb = ttk.Scrollbar(tree_container, orient=tk.HORIZONTAL, command=self.preview_tree.xview)
        self.preview_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.preview_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        return page

    # ---------------------------------------------------------
    # Activity Log Page Construction
    # ---------------------------------------------------------
    def _create_activity_log_page(self) -> tk.Frame:
        page = tk.Frame(self.content_container, bg=COLOR_PRIMARY_BG, padx=PAD_LARGE, pady=PAD_LARGE)

        top_row = tk.Frame(page, bg=COLOR_PRIMARY_BG)
        top_row.pack(fill=tk.X, pady=(0, PAD_MEDIUM))

        tk.Label(top_row, text="Activity Log", font=FONT_TITLE, bg=COLOR_PRIMARY_BG, fg=COLOR_TEXT_PRIMARY).pack(side=tk.LEFT)

        btn_box = tk.Frame(top_row, bg=COLOR_PRIMARY_BG)
        btn_box.pack(side=tk.RIGHT)

        ttk.Button(btn_box, text="Refresh Log", command=self.refresh_log_table).pack(side=tk.LEFT, padx=(0, PAD_SMALL))
        ttk.Button(btn_box, text="Clear Log", command=self.on_clear_log).pack(side=tk.LEFT, padx=(0, PAD_SMALL))
        ttk.Button(btn_box, text="Open Logs Folder", command=lambda: open_folder_in_explorer(LOGS_DIR)).pack(side=tk.LEFT)

        # Log Treeview Container
        tree_container = tk.Frame(page, bg=COLOR_SURFACE, highlightthickness=1, highlightbackground=COLOR_BORDER)
        tree_container.pack(fill=tk.BOTH, expand=True)

        columns = ("timestamp", "action", "filename", "destination", "status", "message")
        self.log_tree = ttk.Treeview(tree_container, columns=columns, show="headings", selectmode="browse")

        self.log_tree.heading("timestamp", text="Timestamp", command=lambda: self._sort_treeview(self.log_tree, "timestamp", False))
        self.log_tree.heading("action", text="Action", command=lambda: self._sort_treeview(self.log_tree, "action", False))
        self.log_tree.heading("filename", text="Filename", command=lambda: self._sort_treeview(self.log_tree, "filename", False))
        self.log_tree.heading("destination", text="Destination", command=lambda: self._sort_treeview(self.log_tree, "destination", False))
        self.log_tree.heading("status", text="Status", command=lambda: self._sort_treeview(self.log_tree, "status", False))
        self.log_tree.heading("message", text="Message", command=lambda: self._sort_treeview(self.log_tree, "message", False))

        self.log_tree.column("timestamp", width=140, minwidth=120)
        self.log_tree.column("action", width=80, minwidth=70)
        self.log_tree.column("filename", width=160, minwidth=120)
        self.log_tree.column("destination", width=220, minwidth=160)
        self.log_tree.column("status", width=90, minwidth=70)
        self.log_tree.column("message", width=220, minwidth=150)

        self.log_tree.tag_configure("evenrow", background=COLOR_SURFACE)
        self.log_tree.tag_configure("oddrow", background=COLOR_TREEVIEW_ALT)

        vsb = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.log_tree.yview)
        hsb = ttk.Scrollbar(tree_container, orient=tk.HORIZONTAL, command=self.log_tree.xview)
        self.log_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.log_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        return page

    # ---------------------------------------------------------
    # About Page Construction
    # ---------------------------------------------------------
    def _create_about_page(self) -> tk.Frame:
        page = tk.Frame(self.content_container, bg=COLOR_PRIMARY_BG, padx=PAD_LARGE, pady=PAD_LARGE)

        tk.Label(page, text="About Smart File Organizer", font=FONT_TITLE, bg=COLOR_PRIMARY_BG, fg=COLOR_TEXT_PRIMARY).pack(anchor="w", pady=(0, PAD_MEDIUM))

        card = tk.Frame(page, bg=COLOR_SURFACE, highlightthickness=1, highlightbackground=COLOR_BORDER, padx=PAD_LARGE, pady=PAD_LARGE)
        card.pack(fill=tk.BOTH, expand=True)

        desc = (
            "Smart File Organizer is an offline desktop utility designed to scan user-selected "
            "directories and categorize files into organized subfolders by file extension.\n"
            "The system previews every operation before execution and provides duplicate resolution "
            "to guarantee that files are never deleted or overwritten."
        )
        tk.Label(card, text=desc, font=FONT_BODY, bg=COLOR_SURFACE, fg=COLOR_TEXT_PRIMARY, wraplength=650, justify="left").pack(anchor="w", pady=(0, PAD_LARGE))

        tk.Label(card, text="Safety Guarantees:", font=FONT_HEADING, bg=COLOR_SURFACE, fg=COLOR_TEXT_PRIMARY).pack(anchor="w", pady=(0, PAD_SMALL))

        guarantees = [
            "- Zero deletion: The application contains no file deletion API calls.",
            "- Zero overwrite: Name collisions are resolved by appending numeric counters.",
            "- Mandatory preview: Proposed moves are visible and verified before any disk modification.",
            "- Safe scope: Subfolders are excluded by default, and system-critical folders are rejected.",
            "- Audit trail: Every action and failure is written to CSV logs and JSON summary reports.",
        ]
        for g in guarantees:
            tk.Label(card, text=g, font=FONT_BODY, bg=COLOR_SURFACE, fg=COLOR_TEXT_SECONDARY, justify="left").pack(anchor="w", pady=2)

        # Runtime environment info
        tk.Label(card, text="Runtime Environment:", font=FONT_HEADING, bg=COLOR_SURFACE, fg=COLOR_TEXT_PRIMARY).pack(anchor="w", pady=(PAD_LARGE, PAD_SMALL))

        py_ver = f"Python Version: {sys.version.split()[0]}"
        tk_ver = f"Tkinter Version: {tk.TkVersion}"
        platform_info = f"Operating System: {sys.platform}"

        tk.Label(card, text=f"{py_ver}  |  {tk_ver}  |  {platform_info}", font=FONT_MONO, bg=COLOR_SURFACE, fg=COLOR_TEXT_SECONDARY).pack(anchor="w")

        return page

    # ---------------------------------------------------------
    # Core Operations and Event Handlers
    # ---------------------------------------------------------
    def _bind_events(self) -> None:
        # Enable Enter key activation for Browse button
        self.browse_btn.bind("<Return>", lambda event: self.on_browse_folder())

    def on_browse_folder(self) -> None:
        """Prompt user for a folder and initiate validation and scanning."""
        if self.is_running:
            return

        chosen = filedialog.askdirectory(title="Select Folder to Organize", parent=self.root)
        if not chosen:
            return

        folder_path = Path(chosen)
        is_valid, error_message = validate_folder(folder_path)
        if not is_valid:
            messagebox.showerror(
                "Invalid Folder Selection",
                f"{error_message}\nPlease select a safe, accessible user folder.",
                parent=self.root,
            )
            return

        self.selected_folder = folder_path
        self.path_entry_var.set(str(folder_path))
        self.refresh_btn.configure(state="normal")
        self.on_refresh_scan()

    def on_subfolder_toggle(self) -> None:
        """Trigger re-scan when include subfolders option changes."""
        if self.selected_folder:
            self.on_refresh_scan()

    def on_refresh_scan(self) -> None:
        """Scan selected directory and calculate plan without moving files."""
        if not self.selected_folder:
            return

        self.status_label.configure(text="Scanning selected folder...")
        self.root.update_idletasks()

        include_sub = self.include_subfolders_var.get()
        self.scanned_files = scan_folder(self.selected_folder, include_subfolders=include_sub)
        self.current_plan = build_plan(self.scanned_files, self.selected_folder)

        # Update dashboard stat cards
        total_count = len(self.current_plan)
        self.stat_cards["total"][1].configure(text=str(total_count))
        self.stat_cards["moved"][1].configure(text="0")
        self.stat_cards["skipped"][1].configure(text="0")
        self.stat_cards["failed"][1].configure(text="0")

        # Update category counts
        cat_counts: Dict[str, int] = {cat: 0 for cat in ALL_CATEGORIES}
        for item in self.current_plan:
            cat = item["category"]
            cat_counts[cat] = cat_counts.get(cat, 0) + 1

        for cat, lbl in self.category_count_labels.items():
            lbl.configure(text=str(cat_counts.get(cat, 0)))

        # Update action buttons state
        if total_count > 0:
            self.preview_btn.configure(state="normal")
            self.organize_btn.configure(state="normal")
            self.preview_organize_now_btn.configure(state="normal")
            self.status_label.configure(text=f"Scan complete: {total_count} files ready to organize.")
        else:
            self.preview_btn.configure(state="disabled")
            self.organize_btn.configure(state="disabled")
            self.preview_organize_now_btn.configure(state="disabled")
            self.status_label.configure(text="Scan complete: No eligible files found to organize.")

        self.refresh_preview_table()

    def refresh_preview_table(self) -> None:
        """Populate the Preview page table with current planned operations."""
        for row_id in self.preview_tree.get_children():
            self.preview_tree.delete(row_id)

        if not self.current_plan:
            self.preview_summary_label.configure(text="No files scheduled to be moved.")
            return

        renamed_count = sum(1 for entry in self.current_plan if entry.get("is_renamed", False))
        total_count = len(self.current_plan)

        summary_msg = f"{total_count} files will be moved. {renamed_count} will be renamed to avoid overwriting."
        self.preview_summary_label.configure(text=summary_msg)

        for i, entry in enumerate(self.current_plan):
            tag = "renamed" if entry.get("is_renamed") else ("evenrow" if i % 2 == 0 else "oddrow")
            self.preview_tree.insert(
                "",
                tk.END,
                values=(
                    entry["filename"],
                    entry["extension"],
                    entry["category"],
                    str(entry["destination"]),
                ),
                tags=(tag,),
            )

    def on_click_preview(self) -> None:
        """Switch view to the Preview page."""
        self.show_page("preview")

    def on_click_organize(self) -> None:
        """Validate, prompt confirmation, and launch background move execution."""
        if not self.selected_folder or not self.current_plan:
            messagebox.showwarning(
                "No Files to Organize",
                "Please select a folder with files before organizing.",
                parent=self.root,
            )
            return

        if self.is_running:
            return

        # Mandatory confirmation dialog
        file_count = len(self.current_plan)
        confirm = messagebox.askyesno(
            "Confirm File Organization",
            f"Are you sure you want to organize {file_count} files in:\n{self.selected_folder}?\n\n"
            "Files will be sorted into category subfolders. No files will be deleted or overwritten.",
            parent=self.root,
        )
        if not confirm:
            return

        # Prepare UI for background run
        self.is_running = True
        self.cancel_flag.clear()
        self.browse_btn.configure(state="disabled")
        self.refresh_btn.configure(state="disabled")
        self.preview_btn.configure(state="disabled")
        self.organize_btn.configure(state="disabled")
        self.preview_organize_now_btn.configure(state="disabled")
        self.cancel_btn.configure(state="normal")
        self.progressbar["value"] = 0
        self.progressbar["maximum"] = file_count

        # Start execution thread
        worker = threading.Thread(
            target=self._run_organize_worker,
            args=(self.current_plan, self.selected_folder),
            daemon=True,
        )
        worker.start()

    def _run_organize_worker(self, plan: List[Dict[str, Any]], root_folder: Path) -> None:
        """Worker thread executing plan and reporting progress through the queue."""
        def progress_callback(cur: int, total: int, msg: str) -> None:
            self.work_queue.put(("progress", (cur, total, msg)))

        def cancel_check() -> bool:
            return self.cancel_flag.is_set()

        try:
            results = execute_plan(
                plan=plan,
                root_folder=root_folder,
                progress_callback=progress_callback,
                cancel_check=cancel_check,
            )
            self.work_queue.put(("done", results))
        except Exception as err:
            self.work_queue.put(("error", str(err)))

    def _poll_work_queue(self) -> None:
        """Poll the background queue on the main UI thread to update controls safely."""
        try:
            while not self.work_queue.empty():
                msg_type, payload = self.work_queue.get_nowait()

                if msg_type == "progress":
                    cur, total, msg = payload
                    self.progressbar["value"] = cur
                    self.status_label.configure(text=msg)

                elif msg_type == "done":
                    self._on_execution_completed(payload)

                elif msg_type == "error":
                    self._on_execution_error(payload)

        except queue.Empty:
            pass

        self.root.after(100, self._poll_work_queue)

    def _on_execution_completed(self, results: Dict[str, Any]) -> None:
        """Handle execution finish: reset controls and present summary dialog."""
        self.is_running = False
        self.cancel_btn.configure(state="disabled")
        self.browse_btn.configure(state="normal")
        self.refresh_btn.configure(state="normal")

        # Update stat numbers with actual results
        self.stat_cards["moved"][1].configure(text=str(results.get("moved", 0)))
        self.stat_cards["skipped"][1].configure(text=str(results.get("skipped", 0)))
        self.stat_cards["failed"][1].configure(text=str(results.get("failed", 0)))

        # Update category count displays
        cat_counts: Dict[str, int] = results.get("category_counts", {})
        for cat, lbl in self.category_count_labels.items():
            lbl.configure(text=str(cat_counts.get(cat, 0)))

        self.status_label.configure(text="Organization run completed.")
        self.progressbar["value"] = self.progressbar["maximum"]

        # Clear plan and refresh preview
        self.current_plan = []
        self.refresh_preview_table()

        # Display modal summary dialog
        SummaryDialog(self.root, results)

    def _on_execution_error(self, err_msg: str) -> None:
        self.is_running = False
        self.cancel_btn.configure(state="disabled")
        self.browse_btn.configure(state="normal")
        self.refresh_btn.configure(state="normal")
        self.status_label.configure(text=f"Execution error: {err_msg}")
        messagebox.showerror("Execution Error", f"An unexpected error occurred: {err_msg}", parent=self.root)

    def on_click_cancel(self) -> None:
        """Request safe termination after current file finishes moving."""
        if self.is_running:
            self.cancel_flag.set()
            self.cancel_btn.configure(state="disabled")
            self.status_label.configure(text="Cancelling... finishing current file.")

    # ---------------------------------------------------------
    # Activity Log Operations
    # ---------------------------------------------------------
    def refresh_log_table(self) -> None:
        """Reload and display the latest records from the activity CSV file."""
        for row_id in self.log_tree.get_children():
            self.log_tree.delete(row_id)

        records = read_log()
        for i, row in enumerate(records):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.log_tree.insert(
                "",
                tk.END,
                values=(
                    row.get("timestamp", ""),
                    row.get("action", ""),
                    row.get("filename", ""),
                    row.get("destination", ""),
                    row.get("status", ""),
                    row.get("message", ""),
                ),
                tags=(tag,),
            )

    def on_clear_log(self) -> None:
        """Clear the CSV activity log after confirmation."""
        confirm = messagebox.askyesno(
            "Clear Activity Log",
            "Are you sure you want to clear the activity log? This cannot be undone.",
            parent=self.root,
        )
        if confirm:
            if clear_log():
                self.refresh_log_table()
                messagebox.showinfo("Log Cleared", "The activity log has been reset.", parent=self.root)
            else:
                messagebox.showerror("Log Error", "Could not clear the log file. It may be locked.", parent=self.root)

    def _sort_treeview(self, tree: ttk.Treeview, col: str, reverse: bool) -> None:
        """Sort Treeview column alphabetically or numerically."""
        items = [(tree.set(k, col), k) for k in tree.get_children("")]
        try:
            # Attempt numeric sort if applicable
            items.sort(key=lambda t: float(t[0]), reverse=reverse)
        except ValueError:
            items.sort(key=lambda t: t[0].lower(), reverse=reverse)

        for index, (_, k) in enumerate(items):
            tree.move(k, "", index)
            tag = "evenrow" if index % 2 == 0 else "oddrow"
            tree.item(k, tags=(tag,))

        tree.heading(col, command=lambda: self._sort_treeview(tree, col, not reverse))


def handle_uncaught_exception(exc_type: Any, exc_value: Any, exc_traceback: Any) -> None:
    """Global exception handler to capture unhandled errors gracefully."""
    error_msg = f"{exc_type.__name__}: {str(exc_value)}"
    log_event("UNCAUGHT_EXCEPTION", "", "", "", "FAILED", error_msg)
    messagebox.showerror(
        "Application Error",
        f"An unexpected error occurred:\n{error_msg}\n\nDetails have been logged to the activity log.",
    )
