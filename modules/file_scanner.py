from pathlib import Path
import csv
import json
from datetime import datetime

IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".tiff", ".tif", ".heic", ".heif", ".avif"
}

VIDEO_EXTENSIONS = {
    ".mp4", ".mov", ".avi", ".mkv", ".webm", ".flv", ".wmv", ".m4v", ".mpeg", ".mpg", ".3gp", ".ts"
}

AUDIO_EXTENSIONS = {
    ".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg", ".wma"
}


def classify_file(file_path: Path) -> str:
    ext = file_path.suffix.lower()

    if ext in IMAGE_EXTENSIONS:
        return "image"

    if ext in VIDEO_EXTENSIONS:
        return "video"

    if ext in AUDIO_EXTENSIONS:
        return "audio"

    return "other"


def scan_media_folder(input_folder: str = "input_media"):
    folder = Path(input_folder)
    results = []

    for file_path in folder.rglob("*"):
        if file_path.is_file():
            stat = file_path.stat()

            results.append({
                "file_name": file_path.name,
                "relative_path": str(file_path.relative_to(folder)),
                "full_path": str(file_path.resolve()),
                "file_type": classify_file(file_path),
                "extension": file_path.suffix.lower(),
                "size_mb": round(stat.st_size / (1024 * 1024), 3),
                "modified_time": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            })

    return results


def export_inventory(results, output_folder: str = "output"):
    output_dir = Path(output_folder)
    output_dir.mkdir(exist_ok=True)

    csv_path = output_dir / "media_inventory.csv"
    json_path = output_dir / "media_inventory.json"

    if results:
        fieldnames = list(results[0].keys())

        with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    else:
        with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["message"])
            writer.writerow(["No media files found."])

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)

    return csv_path, json_path
