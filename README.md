# Smart File Organizer: An Automated Desktop File Management System

## 1. Project Introduction

Smart File Organizer is a standalone desktop application developed in Python to automate the organization of cluttered directories. Users select a target folder, inspect a complete preview of planned operations, and sort files into structured category subfolders based on their extensions. The application adheres to strict safety principles: it never deletes files, never overwrites existing data, and never truncates content. Built entirely with the Python standard library, the application runs seamlessly across Windows 10/11, macOS, and Linux without external third-party dependencies.

## 2. Problem Statement

Computer users frequently accumulate hundreds of disparate files in default locations such as Downloads, Desktop, or shared project directories. Manual sorting is repetitive, time-consuming, and prone to human error, such as accidental file overwrites or unintended deletions. Existing commercial tools often bundle unnecessary telemetry, cloud dependencies, or complex background services. Students and general users require a lightweight, transparent, and completely offline desktop utility that reliably categorizes files while guaranteeing zero data loss.

## 3. Objectives

- Automate file sorting into nine standardized category folders based on file extensions.
- Provide a mandatory preview phase so users verify all proposed moves prior to modifying disk contents.
- Implement collision-proof duplicate resolution using sequential numeric suffixes, such as "report (1).pdf".
- Guarantee complete file preservation by eliminating all deletion, unlinking, and truncation API calls.
- Maintain an asynchronous architecture using background threading to keep the graphical interface responsive.
- Provide a complete audit trail through CSV activity logs and timestamped JSON summary reports.
- Deliver clear, maintainable code using exclusively the Python standard library for academic demonstration and viva defense.

## 4. Features

- Extension-Based Categorization: Classifies files into Images, Documents, Videos, Audio, Archives, Code Files, Spreadsheets, Presentations, and Other Files.
- Collision-Free Renaming: Automatically renames conflicting files to prevent overwriting existing files or colliding with batch operations.
- Non-Destructive Operation: File moves are executed one file at a time, with destination paths verified immediately prior to transfer.
- Non-Recursive Default Scan: Restricts operations to top-level folder files by default; includes an optional checkbox for nested subfolder scanning.
- Safety Protections: Automatically rejects system-critical folders including drive roots, Windows directories, Program Files, and user home roots.
- Automatic File Exclusions: Skips hidden files, temporary files, Windows desktop.ini, Thumbs.db, application logs, and application source code.
- Responsive Tkinter/ttk Interface: Built with a clam-based rectangular layout, high-contrast dark slate sidebar, and real-time progress updates.
- Interactive Tables: Sortable Treeviews with alternating row colors on both Preview and Activity Log screens.
- Post-Execution Summary Dialog: Displays run metrics, duration, category breakdowns, and a scrollable failure log with an Open Folder action.
- Resilient Error Handling: Catches permission errors, missing files, and OS exceptions on a per-file basis so a single failure never stops the batch.

## 5. Technologies Used

- Programming Language: Python 3.10 or newer.
- User Interface: Tkinter and ttk (built-in standard library GUI toolkit).
- File System Operations: pathlib.Path and shutil.move.
- Concurrency and Synchronization: threading.Thread, threading.Lock, threading.Event, and queue.Queue.
- Data Serialization and Logging: csv and json modules.
- Temporal Tracking: datetime module.
- External Dependencies: None (zero third-party packages required).

## 6. Project Structure

```text
smart-file-organizer/
    main.py                      entry point, starts the GUI
    gui.py                       all Tkinter/ttk interface code
    organizer.py                 scanning, planning and moving logic (no GUI code)
    logger.py                    activity log (CSV) and summary report (JSON)
    config.py                    categories, extension map, constants, colors, fonts
    requirements.txt             states that only the standard library is required
    README.md                    project documentation and viva guide
    .gitignore                   ignores logs/, cache, and temporary test folders
    tools/
        make_sample_folder.py    creates a safe test folder with dummy files
    logs/                        created automatically at runtime, holds CSV and JSON reports
```

## 7. Installation Instructions

### Prerequisites for Windows 10/11
1. Download Python 3.10 or newer from the official python.org website.
2. During installation, make sure to check the box labeled "Add Python to PATH".
3. Note that Tkinter is bundled automatically with official Python Windows installers.
4. Verify your installation by opening Command Prompt or PowerShell and running:
   ```powershell
   python --version
   ```

### Project Setup
1. Download or clone this repository to your local computer.
2. Open a terminal or PowerShell prompt and navigate into the project directory:
   ```powershell
   cd "C:\path\to\smart-file-organizer"
   ```
3. Verify that no external packages are needed:
   ```powershell
   type requirements.txt
   ```

## 8. How to Run

Launch the application by executing `main.py` with Python:

```powershell
python main.py
```

## 9. How to Use the Application

1. Open the Application: Run `python main.py`. The window opens centered on your screen displaying the Dashboard.
2. Select a Folder: Click Browse Folder and choose the folder.
3. Review Initial Scan: The dashboard displays the total file count and detected file distribution across the nine categories.
4. Optional Subfolder Inclusion: Check "Include subfolders" if you wish to collect files from nested folders (category folders will never be descended into).
5. Inspect Preview: Click "Preview" to switch to the Preview table. Review source paths, categories, and final destination names. Any duplicate file marked for numeric renaming will be highlighted.
6. Execute Organization: Click "Organize Files" (from Dashboard) or "Organize Now" (from Preview). Confirm the action in the prompt dialog.
7. Monitor Progress: Track the real-time progress bar and status message at the bottom of the window. Click "Cancel" if you wish to safely halt execution after the current file.
8. Inspect Summary: When execution completes, a modal summary dialog displays duration, moved counts, skipped counts, failures, and an "Open Folder" button.
9. Review Activity Log: Switch to the "Activity Log" page in the sidebar to view timestamped audit records or open the `logs/` directory.

## 10. Example Output

### Example Preview Table
```text
Filename              Extension   Category        Destination Path
-------------------------------------------------------------------------------------------------------------------------------
vacation.JPG          .jpg        Images          C:\Users\Student\Desktop\sample_test_folder\Images\vacation.JPG
meeting_notes.txt     .txt        Documents       C:\Users\Student\Desktop\sample_test_folder\Documents\meeting_notes.txt
report.pdf            .pdf        Documents       C:\Users\Student\Desktop\sample_test_folder\Documents\report (1).pdf
quarterly.xlsx        .xlsx       Spreadsheets    C:\Users\Student\Desktop\sample_test_folder\Spreadsheets\quarterly.xlsx
script.py             .py         Code Files      C:\Users\Student\Desktop\sample_test_folder\Code Files\script.py
firmware.bin          .bin        Other Files     C:\Users\Student\Desktop\sample_test_folder\Other Files\firmware.bin
```

### Example Summary Report (JSON excerpt from logs/report_20261014_013000.json)
```json
{
  "folder": "C:\\Users\\Student\\Desktop\\sample_test_folder",
  "start_time": "2026-10-14 01:30:00",
  "end_time": "2026-10-14 01:30:02",
  "total_files": 25,
  "moved": 24,
  "skipped": 1,
  "failed": 0,
  "category_counts": {
    "Images": 4,
    "Documents": 4,
    "Videos": 2,
    "Audio": 2,
    "Archives": 2,
    "Code Files": 4,
    "Spreadsheets": 2,
    "Presentations": 2,
    "Other Files": 2
  },
  "failures": []
}
```

### Example Activity Log (CSV excerpt from logs/activity_log.csv)
*(Note: The SKIP entry below occurs when "Include subfolders" is enabled and scans the existing file in Documents/report.pdf)*
```csv
timestamp,action,filename,source,destination,status,message
2026-10-14 01:30:00,SESSION_START,C:\Users\Student\Desktop\sample_test_folder,,,INFO,Beginning organization of 25 planned items.
2026-10-14 01:30:00,MOVE,vacation.JPG,C:\Users\Student\Desktop\sample_test_folder\vacation.JPG,C:\Users\Student\Desktop\sample_test_folder\Images\vacation.JPG,SUCCESS,Moved successfully.
2026-10-14 01:30:01,MOVE,report.pdf,C:\Users\Student\Desktop\sample_test_folder\report.pdf,C:\Users\Student\Desktop\sample_test_folder\Documents\report (1).pdf,SUCCESS,Moved successfully.
2026-10-14 01:30:01,SKIP,report.pdf,C:\Users\Student\Desktop\sample_test_folder\Documents\report.pdf,C:\Users\Student\Desktop\sample_test_folder\Documents\report.pdf,SKIPPED,File is already in its designated category folder.
2026-10-14 01:30:02,SESSION_END,C:\Users\Student\Desktop\sample_test_folder,,,INFO,Run complete. Moved: 24, Skipped: 1, Failed: 0.
```

## 11. Safe Testing with the Sample Folder

Notice: Always test the application using the generated sample test folder first. Never select your live Documents or Desktop folders for initial verification.

Follow these step-by-step instructions to test:

1. Generate Test Data:
   Open a terminal and run the sample folder generator:
   ```powershell
   python tools/make_sample_folder.py
   ```
   This creates a folder named `sample_test_folder` populated with safe dummy files covering every category, uppercase extensions (.JPG, .Pdf), files with no extension, an existing duplicate (`Documents/report.pdf` vs root `report.pdf`), hidden files, and desktop.ini.

2. Launch Application:
   ```powershell
   python main.py
   ```

3. Select Test Folder:
   Click "Browse Folder" and pick `sample_test_folder`.

4. Preview Moves:
   Click "Preview". Notice:
   - Root `report.pdf` is planned as `Documents/report (1).pdf` to protect the pre-existing file.
   - Hidden file `.hidden_config`, `desktop.ini`, `Thumbs.db`, and temp files are excluded.
   - Files with uppercase extensions (.JPG, .Pdf) map accurately to Images and Documents.
   - Files without extensions map to Other Files.

5. Execute Organization:
   Click "Organize Files" and confirm. Observe the progress bar updating in real time.

6. Inspect Output:
   - Verify that category folders were created.
   - Inspect the Run Summary dialog.
   - Click "Open Folder" to confirm that files reside safely in their new subfolders.
   - Open the "Activity Log" page to view the audit records.

7. Resetting Test Data:
   To perform another test run, re-run:
   ```powershell
   python tools/make_sample_folder.py
   ```

## 12. Limitations

- Extension-Based Classification: Files are categorized purely by suffix; the application does not inspect MIME types or file headers.
- No Automatic Undo: The tool does not currently support one-click reversal of moves, though moves are documented in `activity_log.csv`.
- No Content Inspection: Corrupted files or mislabeled extensions (for example a text file renamed to .jpg) will be categorized according to the extension string.
- No Scheduled Automation: The application is an interactive desktop utility and does not run as a continuous background daemon or cron service.

## 13. Future Enhancements

- Reverse Move (Undo Engine): Read `activity_log.csv` for the latest session to restore files to their exact original paths.
- Custom Rules and Categories: Allow users to create custom categories and define extension mappings via an in-app configuration editor.
- Scheduled Organizing: Add an optional background timer or startup task to organize designated folders periodically.
- Drag-and-Drop Support: Enable direct drag-and-drop of directories into the GUI.
- Appearance Themes: Add user-selectable dark and light visual themes.

## 14. Viva Guide

### Project Overview (150 Words)
Smart File Organizer is a desktop file management utility engineered in Python to sort cluttered directories into designated category folders based on file extensions. Designed with a focus on safety, the application guarantees zero data loss: it contains no file deletion or truncation logic, verifies destination availability before every operation, and resolves naming conflicts using numeric suffixes. The architecture strictly separates business logic in `organizer.py` from the Tkinter/ttk user interface in `gui.py`. Scanning and planning are completed entirely in memory before any disk operations occur. File moves are executed on a dedicated background thread, keeping the GUI responsive while updating a determinate progress bar. Every operation is audited to a CSV activity log, and each session generates a JSON summary report. The application uses only the Python standard library, ensuring full cross-platform compatibility across Windows, macOS, and Linux without external dependencies.

### Viva Questions and Answers

#### Question 1: Why did you choose pathlib instead of os.path?
Answer: `pathlib` provides an object-oriented, cross-platform interface for file system paths. Path objects naturally handle OS-specific path separators (such as backslashes on Windows versus forward slashes on POSIX systems). Properties like `.stem`, `.suffix`, `.parent`, and methods like `.resolve()` make path manipulation readable and less prone to manual string-splitting errors.

#### Question 2: Why do you use shutil.move instead of os.rename?
Answer: `os.rename` fails with an OSError when attempting to move files across different drive partitions or file system mount points. `shutil.move` handles both same-drive and cross-drive transfers. A same-drive move is a single rename, while a cross-drive move copies the data and then removes the original file; neither operation is atomic. In our project, moves are executed one file at a time, with the destination re-checked immediately before each move and each move wrapped in its own try/except block.

#### Question 3: How does duplicate file renaming work?
Answer: In `unique_destination()`, the planner inspects whether the target file already exists on disk or has already been reserved by an earlier item in the planned batch. If a conflict exists, it separates the filename stem and suffix, then enters a loop appending an incrementing numeric counter: `filename (1).ext`, `filename (2).ext`, and so forth, until an unoccupied name is found. This ensures incoming files never overwrite existing files or collide with each other.

#### Question 4: Why is a mandatory preview phase necessary?
Answer: A preview phase prevents unintended user actions. By calculating the complete execution plan in memory and presenting it in a sortable Treeview before modifying disk contents, users can verify exactly which files will be moved, which categories they will enter, and which files will receive duplicate rename suffixes.

#### Question 5: Why did you implement multithreading for file operations?
Answer: In Tkinter, the graphical interface runs on a single main thread handling the event loop (`mainloop()`). If intensive I/O operations like scanning thousands of files or moving data across drives run on the main thread, the window freezes and becomes unresponsive ("Not Responding"). Running the organizer on a background `threading.Thread` with a thread-safe `queue.Queue` keeps the UI responsive, allowing real-time progress updates and safe cancellation.

#### Question 6: How does the extension mapping dictionary work?
Answer: In `config.py`, categories are grouped in `CATEGORY_EXTENSIONS` mapping category names to tuples of lowercase extensions. We also generate an inverted dictionary `EXTENSION_MAP` mapping each extension directly to its category name. This allows `get_category()` to perform O(1) dictionary lookups on the lowercase file extension. Any extension not present in the map automatically falls back to "Other Files".

#### Question 7: What happens if a permission error occurs during execution?
Answer: Each file move is wrapped in an isolated `try...except PermissionError` block. If a file is locked by another process (for example an open Word document) or has restricted permissions, the exception is caught, logged to `activity_log.csv` as a failure with a plain-language explanation, and added to the failure list in the summary report. Crucially, the batch continues processing the remaining files without crashing.

#### Question 8: Why is recursive subfolder scanning turned off by default?
Answer: Recursive descent can unintentionally reorganize deeply nested structures, such as Git repositories, virtual environments (`venv`), or application support folders, scattering dependencies into category folders. Keeping recursion off by default confines operations to the chosen folder. When enabled by the user, the scanner explicitly skips descending into any category folders and ignores files already in their matching category.

#### Question 9: How does the application implement logging and auditing?
Answer: The `logger.py` module maintains two audit mechanisms using standard library tools:
1. `activity_log.csv`: A thread-safe sequential log recording every event with timestamp, action, filename, source, destination, status, and message.
2. `report_YYYYMMDD_HHMMSS.json`: A structured summary report saved at the end of each organize session, storing run metrics, per-category counts, and failure details.

#### Question 10: How are the GUI and business logic separated?
Answer: The architecture strictly follows the separation of concerns. `organizer.py` handles folder scanning, category mapping, plan building, and file movement without importing `tkinter`. It can be run headlessly from command-line scripts or automated test runners. `gui.py` is responsible solely for presentation, user interaction, and dispatching tasks to the background thread.

#### Question 11: What is the time complexity of the folder scanning and planning phase?
Answer: Scanning a folder of N files takes O(N) time because each file name is inspected once. Mapping extensions using a dictionary hash table takes O(1) time per file. Destination resolution takes O(1) average time when no collisions exist, and O(K) where K is the number of duplicate collisions for a specific name. Therefore, the overall planning time complexity is linear, O(N).

#### Question 12: What would the application require to support a full Undo feature?
Answer: An undo feature requires reading the latest session records from `activity_log.csv` in reverse order. For each successfully moved file, the system would verify that the current destination file still exists and that the original source location is unoccupied, then call `shutil.move` to restore the file to its original path, updating the log accordingly.

#### Question 13: How did you test the project to ensure reliability?
Answer: We built a dedicated script `tools/make_sample_folder.py` that populates a safe test folder with edge cases: all 9 categories, mixed-case extensions (.JPG, .Pdf), extensionless files, collision scenarios (duplicate names in root and subfolder), hidden files, Windows system files, and nested folders. We verified planning and execution headlessly and through the GUI without risking user files.

#### Question 14: How does the app prevent accidental deletion of user data?
Answer: By design, the codebase contains zero calls to file deletion APIs: no `os.remove`, `os.unlink`, `shutil.rmtree`, or `Path.unlink`. Furthermore, before every move, destination existence is checked to ensure no overwrite can occur. If a target path is occupied, the move is either renamed during planning or aborted during pre-flight checks.

#### Question 15: How does the global exception handler work?
Answer: Tkinter allows overriding `root.report_callback_exception`. We assign this hook to `handle_uncaught_exception()` in `gui.py`. If an unhandled exception occurs inside any widget callback, instead of printing an unhelpful console traceback or crashing silently, the error is caught, logged to `activity_log.csv`, and displayed in a user-friendly error dialog.

#### Question 16: Why are system-critical directories blocked from selection?
Answer: In `is_system_critical_folder()`, paths such as drive roots (C:\), Windows system folders, Program Files, and user home root directories are validated and rejected. Organizing these directories could inadvertently move operating system files, application binaries, or user profile configurations, causing software instability.
