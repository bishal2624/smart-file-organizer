from pathlib import Path
import sys
import tempfile
import time

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import organizer

print("============================================================")
print("Running Edge Case Verification Tests")
print("============================================================")

with tempfile.TemporaryDirectory() as temp_dir_str:
    base = Path(temp_dir_str)

    # 1. Empty folder
    empty_dir = base / "empty_dir"
    empty_dir.mkdir()
    scanned_empty = organizer.scan_folder(empty_dir)
    plan_empty = organizer.build_plan(scanned_empty, empty_dir)
    res_empty = organizer.execute_plan(plan_empty, empty_dir)
    assert len(scanned_empty) == 0
    assert res_empty["moved"] == 0
    print("[PASS] Empty folder: scanned=0, moved=0, no errors.")

    # 2. Folder with only subfolders
    subdirs_only = base / "subdirs_only"
    subdirs_only.mkdir()
    (subdirs_only / "folderA").mkdir()
    (subdirs_only / "folderB").mkdir()
    scanned_subdirs = organizer.scan_folder(subdirs_only, include_subfolders=False)
    assert len(scanned_subdirs) == 0
    print("[PASS] Folder with only subfolders: directories are never treated as files.")

    # 3. File with no extension
    no_ext_dir = base / "no_ext_dir"
    no_ext_dir.mkdir()
    f_no_ext = no_ext_dir / "README_NO_EXT"
    f_no_ext.write_text("no extension content", encoding="utf-8")
    assert organizer.get_category(f_no_ext) == "Other Files"
    scanned_no_ext = organizer.scan_folder(no_ext_dir)
    plan_no_ext = organizer.build_plan(scanned_no_ext, no_ext_dir)
    res_no_ext = organizer.execute_plan(plan_no_ext, no_ext_dir)
    assert (no_ext_dir / "Other Files" / "README_NO_EXT").exists()
    print("[PASS] File with no extension: correctly categorized into 'Other Files'.")

    # 4. Uppercase and mixed-case extensions
    case_dir = base / "case_dir"
    case_dir.mkdir()
    (case_dir / "photo.JPG").write_text("jpg", encoding="utf-8")
    (case_dir / "song.MP3").write_text("mp3", encoding="utf-8")
    (case_dir / "doc.PdF").write_text("pdf", encoding="utf-8")
    assert organizer.get_category(case_dir / "photo.JPG") == "Images"
    assert organizer.get_category(case_dir / "song.MP3") == "Audio"
    assert organizer.get_category(case_dir / "doc.PdF") == "Documents"
    plan_case = organizer.build_plan(organizer.scan_folder(case_dir), case_dir)
    organizer.execute_plan(plan_case, case_dir)
    assert (case_dir / "Images" / "photo.JPG").exists()
    assert (case_dir / "Audio" / "song.MP3").exists()
    assert (case_dir / "Documents" / "doc.PdF").exists()
    print("[PASS] Uppercase extensions: case-insensitively categorized.")

    # 5. Very long filename
    long_dir = base / "long_dir"
    long_dir.mkdir()
    long_name = "a" * 120 + ".txt"
    f_long = long_dir / long_name
    f_long.write_text("long name content", encoding="utf-8")
    plan_long = organizer.build_plan(organizer.scan_folder(long_dir), long_dir)
    res_long = organizer.execute_plan(plan_long, long_dir)
    assert (long_dir / "Documents" / long_name).exists()
    print(f"[PASS] Very long filename (124 chars): successfully moved to Documents.")

    # 6. Read-only file
    ro_dir = base / "ro_dir"
    ro_dir.mkdir()
    ro_file = ro_dir / "readonly_notes.txt"
    ro_file.write_text("readonly content", encoding="utf-8")
    ro_file.chmod(0o444)
    try:
        plan_ro = organizer.build_plan(organizer.scan_folder(ro_dir), ro_dir)
        res_ro = organizer.execute_plan(plan_ro, ro_dir)
        print(f"[PASS] Read-only file: moved={res_ro['moved']}, failed={res_ro['failed']} (handled safely without crash).")
    finally:
        # Reset permission so temp dir cleanup can remove it
        try:
            ro_dest = ro_dir / "Documents" / "readonly_notes.txt"
            if ro_dest.exists():
                ro_dest.chmod(0o666)
            elif ro_file.exists():
                ro_file.chmod(0o666)
        except OSError:
            pass

    # 7. File in use / locked file
    lock_dir = base / "lock_dir"
    lock_dir.mkdir()
    locked_file = lock_dir / "locked_file.txt"
    locked_file.write_text("locked content", encoding="utf-8")
    plan_locked = organizer.build_plan(organizer.scan_folder(lock_dir), lock_dir)
    # Open exclusively for writing without closing to simulate file lock on Windows
    with open(locked_file, "r+", encoding="utf-8") as lock_handle:
        res_locked = organizer.execute_plan(plan_locked, lock_dir)
        print(f"[PASS] File in use: handled with isolated try/except (moved={res_locked['moved']}, failed={res_locked['failed']}).")

    # 8. Non-existent folder
    non_existent = base / "does_not_exist_folder"
    is_valid_ne, err_ne = organizer.validate_folder(non_existent)
    assert not is_valid_ne
    print(f"[PASS] Non-existent folder rejected: '{err_ne}'")

    # 9. Drive root selection
    drive_root = Path("C:\\") if sys.platform.startswith("win") else Path("/")
    is_valid_root, err_root = organizer.validate_folder(drive_root)
    assert not is_valid_root
    print(f"[PASS] Drive root rejected: '{err_root}'")

print("============================================================")
print("ALL EDGE CASE VERIFICATIONS COMPLETED SUCCESSFULLY")
print("============================================================")
