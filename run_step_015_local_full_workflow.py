from pathlib import Path
import argparse
import subprocess
import sys
import json
import shutil
from datetime import datetime


PROJECT_ROOT = Path(__file__).resolve().parent
INPUT_DIR = PROJECT_ROOT / "input_media"
OUTPUT_DIR = PROJECT_ROOT / "output"
REPORTS_DIR = OUTPUT_DIR / "reports"
BATCHES_DIR = REPORTS_DIR / "batches"

IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".tiff", ".tif", ".heic", ".heif", ".avif"
}

VIDEO_EXTENSIONS = {
    ".mp4", ".mov", ".avi", ".mkv", ".webm", ".flv", ".wmv", ".m4v", ".mpeg", ".mpg", ".3gp", ".ts"
}


def ensure_folders():
    INPUT_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    BATCHES_DIR.mkdir(parents=True, exist_ok=True)


def count_media_files():
    image_files = []
    video_files = []
    other_files = []

    for file_path in INPUT_DIR.rglob("*"):
        if not file_path.is_file():
            continue

        ext = file_path.suffix.lower()

        if ext in IMAGE_EXTENSIONS:
            image_files.append(file_path)
        elif ext in VIDEO_EXTENSIONS:
            video_files.append(file_path)
        else:
            other_files.append(file_path)

    return image_files, video_files, other_files


def run_command(step_name, command):
    print("")
    print("=" * 80)
    print(step_name)
    print("=" * 80)
    print("Command:", " ".join(command))
    print("")

    process = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore"
    )

    output = ""

    if process.stdout:
        output += process.stdout

    if process.stderr:
        output += "\n[STDERR]\n" + process.stderr

    print(output)

    return {
        "step_name": step_name,
        "command": command,
        "return_code": process.returncode,
        "success": process.returncode == 0,
        "output_preview": output[-3000:],
    }


def normalize_report_format(value):
    value = (value or "").strip().lower()

    if value in ["word", "docx", "1"]:
        return "word"

    if value in ["pdf", "2"]:
        return "pdf"

    if value in ["both", "all", "word+pdf", "3"]:
        return "both"

    return "both"


def build_image_steps(report_format):
    return [
        ("Step 1 | Media inventory scan", [sys.executable, "run_step_001_inventory.py"]),
        ("Step 2 | Image basic information extraction", [sys.executable, "run_step_002_image_info.py"]),
        ("Step 5 | Image OCR extraction", [sys.executable, "run_step_005_image_ocr.py"]),
        ("Step 5D | OCR text cleanup", [sys.executable, "run_step_005d_clean_ocr_text.py"]),
        ("Step 7A | Local AI summary for images", [sys.executable, "run_step_007a_local_ai_summary.py"]),
        ("Step 7A Report | Image local summary report", [sys.executable, "run_step_007a_generate_summary_report.py", "--format", report_format]),
    ]


def build_video_steps():
    return [
        ("Step 9 | Video basic info and preview frames", [sys.executable, "run_step_009_video_info.py"]),
        ("Step 10 | Video audio extraction", [sys.executable, "run_step_010_video_audio_extract.py"]),
        ("Step 11 | Local Whisper video transcription", [sys.executable, "run_step_011_video_transcribe.py"]),
        ("Step 12 | Video transcript summary and report", [sys.executable, "run_step_012_video_summary_report.py"]),
    ]


def archive_reports(report_format, include_images, include_videos):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    batch_dir = BATCHES_DIR / f"local_full_{timestamp}"
    batch_dir.mkdir(parents=True, exist_ok=True)

    expected_files = []

    if include_images:
        if report_format in ["word", "both"]:
            expected_files.append(REPORTS_DIR / "image_ai_summary_local_report.docx")
        if report_format in ["pdf", "both"]:
            expected_files.append(REPORTS_DIR / "image_ai_summary_local_report.pdf")

    if include_videos:
        expected_files.append(REPORTS_DIR / "video_summary_local_report.docx")
        expected_files.append(REPORTS_DIR / "video_summary_local_report.pdf")

    copied = []

    for source in expected_files:
        if source.exists():
            target = batch_dir / f"{timestamp}_{source.name}"
            shutil.copy2(source, target)
            copied.append(str(target))

    return batch_dir, copied


def save_status(status):
    status_json = OUTPUT_DIR / "last_local_full_workflow_status.json"
    status_txt = OUTPUT_DIR / "last_local_full_workflow_status.txt"

    with open(status_json, "w", encoding="utf-8") as f:
        json.dump(status, f, ensure_ascii=False, indent=2)

    with open(status_txt, "w", encoding="utf-8") as f:
        f.write("VIDEO-EXTRACT-015 | Local Full Workflow Status\n")
        f.write("=" * 60 + "\n")
        f.write(f"Generated time: {status.get('generated_time')}\n")
        f.write(f"Report format: {status.get('report_format')}\n")
        f.write(f"Images found: {status.get('images_found')}\n")
        f.write(f"Videos found: {status.get('videos_found')}\n")
        f.write(f"Overall success: {status.get('overall_success')}\n")
        f.write(f"Batch folder: {status.get('batch_folder')}\n")
        f.write("\nSteps:\n")

        for step in status.get("steps", []):
            mark = "OK" if step.get("success") else "FAILED"
            f.write(f"- {mark} | {step.get('step_name')} | return code: {step.get('return_code')}\n")

    return status_json, status_txt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--format",
        default="both",
        help="Image report format: word, pdf, or both. Video report is currently generated as Word + PDF."
    )
    parser.add_argument(
        "--no-batch",
        action="store_true",
        help="Do not archive generated reports into a timestamped batch folder."
    )
    args = parser.parse_args()

    ensure_folders()

    report_format = normalize_report_format(args.format)

    print("=" * 80)
    print("VIDEO-EXTRACT-015 | Local full workflow runner")
    print("=" * 80)
    print(f"Project folder: {PROJECT_ROOT}")
    print(f"Input folder  : {INPUT_DIR}")
    print(f"Output folder : {OUTPUT_DIR}")
    print(f"Reports folder: {REPORTS_DIR}")
    print(f"Image report format: {report_format}")
    print("OpenAI API: disabled for this local workflow")
    print("")

    image_files, video_files, other_files = count_media_files()

    print("Input media summary:")
    print(f"- Images: {len(image_files)}")
    print(f"- Videos: {len(video_files)}")
    print(f"- Other : {len(other_files)}")

    steps_to_run = []

    if image_files:
        steps_to_run.extend(build_image_steps(report_format))
    else:
        print("")
        print("No image files found. Image workflow will be skipped.")

    if video_files:
        steps_to_run.extend(build_video_steps())
    else:
        print("")
        print("No video files found. Video workflow will be skipped.")

    if not steps_to_run:
        print("")
        print("No supported media files found. Please add images or videos into input_media.")
        status = {
            "generated_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "report_format": report_format,
            "images_found": len(image_files),
            "videos_found": len(video_files),
            "overall_success": False,
            "batch_folder": "",
            "steps": [],
            "message": "No supported media files found."
        }
        save_status(status)
        return

    step_results = []
    overall_success = True

    for step_name, command in steps_to_run:
        result = run_command(step_name, command)
        step_results.append(result)

        if not result["success"]:
            overall_success = False
            print("")
            print("Workflow stopped because a step failed.")
            break

    batch_folder = ""
    copied_reports = []

    if overall_success and not args.no_batch:
        batch_dir, copied_reports = archive_reports(
            report_format=report_format,
            include_images=bool(image_files),
            include_videos=bool(video_files)
        )
        batch_folder = str(batch_dir.resolve())

    status = {
        "generated_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "report_format": report_format,
        "images_found": len(image_files),
        "videos_found": len(video_files),
        "other_found": len(other_files),
        "overall_success": overall_success,
        "batch_folder": batch_folder,
        "copied_reports": copied_reports,
        "steps": step_results,
    }

    status_json, status_txt = save_status(status)

    print("")
    print("=" * 80)
    print("LOCAL FULL WORKFLOW SUMMARY")
    print("=" * 80)
    print(f"Overall success: {overall_success}")
    print(f"Images processed: {len(image_files)}")
    print(f"Videos processed: {len(video_files)}")
    print(f"Status JSON: {status_json}")
    print(f"Status TXT : {status_txt}")

    if batch_folder:
        print(f"Batch folder: {batch_folder}")
        print("Copied reports:")
        for item in copied_reports:
            print(f"- {item}")

    print("")
    print("Step 15 completed.")


if __name__ == "__main__":
    main()
