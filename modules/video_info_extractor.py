from pathlib import Path
import csv
import json
from datetime import datetime

import cv2


VIDEO_EXTENSIONS = {
    ".mp4", ".mov", ".avi", ".mkv", ".webm", ".flv", ".wmv", ".m4v", ".mpeg", ".mpg", ".3gp", ".ts"
}


def format_duration(seconds):
    try:
        seconds = float(seconds)
    except Exception:
        return ""

    if seconds <= 0:
        return ""

    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def safe_save_frame(frame, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Use imencode + tofile for better Windows path compatibility.
    success, encoded = cv2.imencode(output_path.suffix, frame)

    if not success:
        return False

    encoded.tofile(str(output_path))
    return True


def extract_preview_frames(video_path: Path, output_root: Path, frame_count, max_frames=3):
    preview_paths = []

    video_name = video_path.stem
    video_frame_dir = output_root / video_name
    video_frame_dir.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(str(video_path))

    if not cap.isOpened():
        return preview_paths

    try:
        if not frame_count or frame_count <= 0:
            candidate_indexes = [0]
        elif frame_count < 3:
            candidate_indexes = [0]
        else:
            candidate_indexes = [
                0,
                int(frame_count * 0.5),
                max(int(frame_count) - 1, 0)
            ]

        # Remove duplicates while keeping order.
        seen = set()
        frame_indexes = []

        for index in candidate_indexes:
            index = int(max(index, 0))
            if index not in seen:
                seen.add(index)
                frame_indexes.append(index)

        for i, frame_index in enumerate(frame_indexes, start=1):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
            success, frame = cap.read()

            if not success or frame is None:
                continue

            frame_path = video_frame_dir / f"preview_{i:02d}_frame_{frame_index}.jpg"

            if safe_save_frame(frame, frame_path):
                preview_paths.append(str(frame_path.resolve()))

    finally:
        cap.release()

    return preview_paths


def extract_single_video_info(file_path: Path, root_folder: Path, frame_output_root: Path):
    stat = file_path.stat()

    result = {
        "file_name": file_path.name,
        "relative_path": str(file_path.relative_to(root_folder)),
        "full_path": str(file_path.resolve()),
        "extension": file_path.suffix.lower(),
        "size_mb": round(stat.st_size / (1024 * 1024), 3),
        "modified_time": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
        "is_readable": False,
        "width": "",
        "height": "",
        "fps": "",
        "frame_count": "",
        "duration_seconds": "",
        "duration_hms": "",
        "preview_frame_count": 0,
        "preview_frames": [],
        "error_message": ""
    }

    cap = cv2.VideoCapture(str(file_path))

    try:
        if not cap.isOpened():
            result["error_message"] = "Video cannot be opened by OpenCV."
            return result

        result["is_readable"] = True

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
        fps = float(cap.get(cv2.CAP_PROP_FPS) or 0)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)

        duration_seconds = 0
        if fps > 0 and frame_count > 0:
            duration_seconds = frame_count / fps

        result["width"] = width
        result["height"] = height
        result["fps"] = round(fps, 3)
        result["frame_count"] = frame_count
        result["duration_seconds"] = round(duration_seconds, 3)
        result["duration_hms"] = format_duration(duration_seconds)

    except Exception as e:
        result["error_message"] = str(e)

    finally:
        cap.release()

    if result["is_readable"]:
        try:
            preview_frames = extract_preview_frames(
                video_path=file_path,
                output_root=frame_output_root,
                frame_count=result["frame_count"],
                max_frames=3
            )
            result["preview_frames"] = preview_frames
            result["preview_frame_count"] = len(preview_frames)
        except Exception as e:
            result["error_message"] = f"{result['error_message']} | Preview frame extraction failed: {e}"

    return result


def extract_batch_video_info(input_folder="input_media", output_folder="output"):
    root_folder = Path(input_folder)
    output_dir = Path(output_folder)
    frame_output_root = output_dir / "video_frames"
    frame_output_root.mkdir(parents=True, exist_ok=True)

    results = []

    for file_path in root_folder.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in VIDEO_EXTENSIONS:
            results.append(
                extract_single_video_info(
                    file_path=file_path,
                    root_folder=root_folder,
                    frame_output_root=frame_output_root
                )
            )

    return results


def export_video_info(results, output_folder="output"):
    output_dir = Path(output_folder)
    output_dir.mkdir(exist_ok=True)

    csv_path = output_dir / "video_basic_info.csv"
    json_path = output_dir / "video_basic_info.json"

    fieldnames = [
        "file_name",
        "relative_path",
        "full_path",
        "extension",
        "size_mb",
        "modified_time",
        "is_readable",
        "width",
        "height",
        "fps",
        "frame_count",
        "duration_seconds",
        "duration_hms",
        "preview_frame_count",
        "preview_frames",
        "error_message"
    ]

    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for item in results:
            row = dict(item)
            row["preview_frames"] = " | ".join(item.get("preview_frames", []))
            writer.writerow(row)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    return csv_path, json_path
