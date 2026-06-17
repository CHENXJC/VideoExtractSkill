from pathlib import Path
import importlib.util
import os
import shutil
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parent


CHECKS = [
    ("streamlit", "streamlit"),
    ("pandas", "pandas"),
    ("Pillow", "PIL"),
    ("python-docx", "docx"),
    ("pywin32", "win32com.client"),
    ("pytesseract", "pytesseract"),
    ("opencv-python", "cv2"),
    ("imageio-ffmpeg", "imageio_ffmpeg"),
    ("faster-whisper", "faster_whisper"),
]


def check_python_package(package_name, import_name):
    spec = importlib.util.find_spec(import_name)
    return spec is not None


def check_path_exists(label, path):
    return label, Path(path).exists(), str(Path(path))


def check_tesseract():
    possible_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ]

    for path in possible_paths:
        if Path(path).exists():
            return True, path

    found = shutil.which("tesseract")
    if found:
        return True, found

    return False, "Tesseract not found"


def check_word_com():
    try:
        import win32com.client
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        word.Quit()
        return True, "Microsoft Word COM available"
    except Exception as e:
        return False, str(e)


def main():
    print("=" * 80)
    print("VIDEO-EXTRACT-016 | Environment Check")
    print("=" * 80)
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Python: {sys.executable}")
    print("")

    all_ok = True

    print("Python package checks:")
    for package_name, import_name in CHECKS:
        ok = check_python_package(package_name, import_name)
        mark = "OK" if ok else "MISSING"
        print(f"- {mark:8} | {package_name}")
        if not ok:
            all_ok = False

    print("")
    print("Folder checks:")
    folders = [
        ("input_media", PROJECT_ROOT / "input_media"),
        ("output", PROJECT_ROOT / "output"),
        ("output/reports", PROJECT_ROOT / "output" / "reports"),
        ("output/reports/batches", PROJECT_ROOT / "output" / "reports" / "batches"),
        ("modules", PROJECT_ROOT / "modules"),
        ("config", PROJECT_ROOT / "config"),
        ("docs", PROJECT_ROOT / "docs"),
        ("assets", PROJECT_ROOT / "assets"),
    ]

    for label, path in folders:
        ok = path.exists()
        mark = "OK" if ok else "MISSING"
        print(f"- {mark:8} | {label} | {path}")
        if not ok:
            all_ok = False

    print("")
    print("External tool checks:")
    tess_ok, tess_msg = check_tesseract()
    print(f"- {'OK' if tess_ok else 'MISSING':8} | Tesseract OCR | {tess_msg}")
    if not tess_ok:
        all_ok = False

    word_ok, word_msg = check_word_com()
    print(f"- {'OK' if word_ok else 'WARNING':8} | Word PDF conversion | {word_msg}")

    print("")
    print("Main script checks:")
    scripts = [
        "app.py",
        "run_step_015_local_full_workflow.py",
        "run_step_011_video_transcribe.py",
        "run_step_012_video_summary_report.py",
    ]

    for script in scripts:
        path = PROJECT_ROOT / script
        ok = path.exists()
        print(f"- {'OK' if ok else 'MISSING':8} | {script}")
        if not ok:
            all_ok = False

    print("")
    print("=" * 80)
    print(f"Environment overall status: {'READY' if all_ok else 'NEEDS ATTENTION'}")
    print("=" * 80)

    if not all_ok:
        print("")
        print("Suggested repair command:")
        print("python -m pip install -r requirements.txt")

    print("")
    print("Step 16 environment check completed.")


if __name__ == "__main__":
    main()
