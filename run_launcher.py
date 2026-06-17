from pathlib import Path
import argparse
import importlib
import os
import shutil
import subprocess
import sys
from datetime import datetime


PROJECT_ROOT = Path(__file__).resolve().parent
LOG_DIR = PROJECT_ROOT / "output" / "logs"

REQUIRED_FOLDERS = [
    "input_media",
    "output",
    "output/reports",
    "output/reports/batches",
    "output/logs",
    "modules",
    "config",
    "docs",
    "assets",
]

REQUIRED_FILES = [
    "app.py",
    "requirements.txt",
    "run_step_015_local_full_workflow.py",
    "run_step_011_video_transcribe.py",
    "run_step_012_video_summary_report.py",
]

REQUIRED_PACKAGES = [
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


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def ensure_folders():
    for folder in REQUIRED_FOLDERS:
        (PROJECT_ROOT / folder).mkdir(parents=True, exist_ok=True)


def check_package(import_name):
    try:
        importlib.import_module(import_name)
        return True, ""
    except Exception as e:
        return False, str(e)


def check_tesseract():
    possible_paths = [
        Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe"),
        Path(r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"),
    ]

    for path in possible_paths:
        if path.exists():
            return True, str(path)

    found = shutil.which("tesseract")
    if found:
        return True, found

    return False, "Tesseract OCR not found"


def check_word_pdf():
    try:
        import win32com.client
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        word.Quit()
        return True, "Microsoft Word COM available"
    except Exception as e:
        return False, str(e)


def run_precheck():
    ensure_folders()

    print("=" * 80)
    print("VIDEO-EXTRACT-017 | Launcher Pre-check")
    print("=" * 80)
    print(f"Time        : {now()}")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Python      : {sys.executable}")
    print("")

    hard_fail = False
    warnings = []

    print("Folder checks:")
    for folder in REQUIRED_FOLDERS:
        path = PROJECT_ROOT / folder
        ok = path.exists()
        print(f"- {'OK' if ok else 'MISSING':8} | {folder}")
        if not ok:
            hard_fail = True

    print("")
    print("Core file checks:")
    for file_name in REQUIRED_FILES:
        path = PROJECT_ROOT / file_name
        ok = path.exists()
        print(f"- {'OK' if ok else 'MISSING':8} | {file_name}")
        if not ok:
            hard_fail = True

    print("")
    print("Python package checks:")
    missing_packages = []

    for package_name, import_name in REQUIRED_PACKAGES:
        ok, msg = check_package(import_name)
        print(f"- {'OK' if ok else 'MISSING':8} | {package_name}")
        if not ok:
            missing_packages.append(package_name)
            hard_fail = True

    print("")
    print("External tool checks:")

    tess_ok, tess_msg = check_tesseract()
    print(f"- {'OK' if tess_ok else 'MISSING':8} | Tesseract OCR | {tess_msg}")
    if not tess_ok:
        hard_fail = True

    word_ok, word_msg = check_word_pdf()
    print(f"- {'OK' if word_ok else 'WARNING':8} | Word PDF conversion | {word_msg}")
    if not word_ok:
        warnings.append("Microsoft Word COM is not available. PDF export may fail, but Word export can still work.")

    print("")
    print("=" * 80)

    if hard_fail:
        print("Launcher status: NEEDS ATTENTION")
        print("=" * 80)

        if missing_packages:
            print("")
            print("Missing Python packages detected.")
            print("Suggested repair command:")
            print("python -m pip install -r requirements.txt")

        print("")
        print("Please run Repair_Environment.cmd or fix the missing items above.")
        return False

    print("Launcher status: READY")
    print("=" * 80)

    if warnings:
        print("")
        print("Warnings:")
        for item in warnings:
            print(f"- {item}")

    return True


def write_launcher_log(title, return_code):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / "launcher_last_status.txt"

    with open(log_path, "w", encoding="utf-8") as f:
        f.write("VIDEO-EXTRACT Launcher Status\n")
        f.write("=" * 60 + "\n")
        f.write(f"Time: {now()}\n")
        f.write(f"Action: {title}\n")
        f.write(f"Return code: {return_code}\n")

    return log_path


def start_streamlit_app():
    print("")
    print("Starting Batch Media Insight Extractor web app...")
    print("Browser should open at: http://localhost:8501")
    print("")

    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "app.py",
    ]

    return subprocess.call(command, cwd=PROJECT_ROOT)


def run_local_full_workflow():
    print("")
    print("Running local full workflow...")
    print("")

    command = [
        sys.executable,
        "run_step_015_local_full_workflow.py",
        "--format",
        "both",
    ]

    return subprocess.call(command, cwd=PROJECT_ROOT)


def repair_environment():
    print("=" * 80)
    print("VIDEO-EXTRACT-017 | Repair Environment")
    print("=" * 80)

    ensure_folders()

    requirements = PROJECT_ROOT / "requirements.txt"

    if not requirements.exists():
        print("requirements.txt not found.")
        return 1

    print("Installing requirements...")
    print("")

    command = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "-r",
        str(requirements),
    ]

    code = subprocess.call(command, cwd=PROJECT_ROOT)

    print("")
    print("Repair command completed.")
    print(f"Return code: {code}")
    return code


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--start-app", action="store_true")
    parser.add_argument("--run-full", action="store_true")
    parser.add_argument("--repair", action="store_true")
    args = parser.parse_args()

    if args.repair:
        code = repair_environment()
        write_launcher_log("repair", code)
        sys.exit(code)

    ready = run_precheck()

    if args.check_only:
        write_launcher_log("check-only", 0 if ready else 1)
        sys.exit(0 if ready else 1)

    if not ready:
        write_launcher_log("precheck-failed", 1)
        sys.exit(1)

    if args.start_app:
        code = start_streamlit_app()
        write_launcher_log("start-app", code)
        sys.exit(code)

    if args.run_full:
        code = run_local_full_workflow()
        write_launcher_log("run-full", code)
        sys.exit(code)

    write_launcher_log("check", 0)
    sys.exit(0)


if __name__ == "__main__":
    main()
