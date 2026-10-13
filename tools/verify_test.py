from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import organizer
import logger

test_dir = Path("sample_test_folder").resolve()

# 1. Count files before
all_files_before = [p for p in test_dir.rglob("*") if p.is_file()]
count_before = len(all_files_before)
print(f"Total files before organize: {count_before}")

# 2. Run headless scan and plan
scanned = organizer.scan_folder(test_dir, include_subfolders=False)
plan = organizer.build_plan(scanned, test_dir)
print(f"Files scanned for organization: {len(scanned)}")
print(f"Planned operations count: {len(plan)}")

# Check duplicate plan entry
renamed_entries = [e for e in plan if e.get("is_renamed")]
for r in renamed_entries:
    print(f"Duplicate detected and resolved: {r['filename']} -> {r['dest_filename']}")

# 3. Execute plan
results = organizer.execute_plan(plan, test_dir)
print(f"Execution Results: Moved={results['moved']}, Skipped={results['skipped']}, Failed={results['failed']}")

# 4. Count files after
all_files_after = [p for p in test_dir.rglob("*") if p.is_file()]
count_after = len(all_files_after)
print(f"Total files after organize: {count_after}")

# 5. Assertions
assert count_before == count_after, f"File count mismatch! Before: {count_before}, After: {count_after}"
print("ASSERTION PASSED: File count before equals file count after (zero deletion).")

# Verify duplicate protection
doc_orig = test_dir / "Documents" / "report.pdf"
doc_renamed = test_dir / "Documents" / "report (1).pdf"
assert doc_orig.exists(), "Original Documents/report.pdf is missing!"
assert doc_renamed.exists(), "Renamed duplicate Documents/report (1).pdf is missing!"
print("ASSERTION PASSED: Duplicate resolution verified; report (1).pdf created without overwriting original.")

# Verify exclusions remain in root
assert (test_dir / ".hidden_config").exists(), "Hidden file was moved or deleted!"
assert (test_dir / "desktop.ini").exists(), "desktop.ini was moved or deleted!"
assert (test_dir / "Thumbs.db").exists(), "Thumbs.db was moved or deleted!"
assert (test_dir / "~$draft_document.docx").exists(), "Temporary file was moved or deleted!"
assert (test_dir / "scratch_cache.tmp").exists(), "Tmp file was moved or deleted!"
print("ASSERTION PASSED: Excluded hidden, system, and temporary files remained in root untouched.")

# Verify subfolder untouched by default
assert (test_dir / "project_subfolder" / "nested_notes.txt").exists(), "Subfolder contents were altered!"
print("ASSERTION PASSED: Nested subfolder contents untouched by default.")

# Verify uppercase extension categorization
assert (test_dir / "Images" / "vacation.JPG").exists(), "vacation.JPG not in Images!"
assert (test_dir / "Documents" / "manual.Pdf").exists(), "manual.Pdf not in Documents!"
print("ASSERTION PASSED: Mixed-case extensions correctly categorized.")

# Verify extensionless categorization
assert (test_dir / "Other Files" / "LICENSE_NO_EXTENSION").exists(), "LICENSE_NO_EXTENSION not in Other Files!"
print("ASSERTION PASSED: File without extension correctly placed in Other Files.")
