from pathlib import Path
import csv
import json
from datetime import datetime

from PIL import Image, ExifTags

try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except Exception:
    pass


IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".tiff", ".tif", ".heic", ".heif", ".avif"
}


def get_exif_basic(image: Image.Image) -> dict:
    exif_result = {
        "has_exif": False,
        "exif_datetime": "",
        "camera_make": "",
        "camera_model": "",
        "software": "",
        "orientation": ""
    }

    try:
        exif_data = image.getexif()

        if not exif_data:
            return exif_result

        readable_exif = {}

        for tag_id, value in exif_data.items():
            tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
            readable_exif[tag_name] = str(value)

        exif_result["has_exif"] = True
        exif_result["exif_datetime"] = readable_exif.get("DateTime", "")
        exif_result["camera_make"] = readable_exif.get("Make", "")
        exif_result["camera_model"] = readable_exif.get("Model", "")
        exif_result["software"] = readable_exif.get("Software", "")
        exif_result["orientation"] = readable_exif.get("Orientation", "")

        return exif_result

    except Exception:
        return exif_result


def extract_single_image_info(file_path: Path, root_folder: Path) -> dict:
    stat = file_path.stat()

    base_result = {
        "file_name": file_path.name,
        "relative_path": str(file_path.relative_to(root_folder)),
        "full_path": str(file_path.resolve()),
        "extension": file_path.suffix.lower(),
        "size_mb": round(stat.st_size / (1024 * 1024), 3),
        "modified_time": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
        "is_readable": False,
        "image_format": "",
        "width": "",
        "height": "",
        "mode": "",
        "has_exif": False,
        "exif_datetime": "",
        "camera_make": "",
        "camera_model": "",
        "software": "",
        "orientation": "",
        "error_message": ""
    }

    try:
        with Image.open(file_path) as img:
            base_result["is_readable"] = True
            base_result["image_format"] = img.format or ""
            base_result["width"] = img.width
            base_result["height"] = img.height
            base_result["mode"] = img.mode or ""

            exif_info = get_exif_basic(img)
            base_result.update(exif_info)

    except Exception as e:
        base_result["error_message"] = str(e)

    return base_result


def extract_batch_image_info(input_folder: str = "input_media"):
    root_folder = Path(input_folder)
    results = []

    for file_path in root_folder.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in IMAGE_EXTENSIONS:
            results.append(extract_single_image_info(file_path, root_folder))

    return results


def export_image_info(results, output_folder: str = "output"):
    output_dir = Path(output_folder)
    output_dir.mkdir(exist_ok=True)

    csv_path = output_dir / "image_basic_info.csv"
    json_path = output_dir / "image_basic_info.json"

    fieldnames = [
        "file_name",
        "relative_path",
        "full_path",
        "extension",
        "size_mb",
        "modified_time",
        "is_readable",
        "image_format",
        "width",
        "height",
        "mode",
        "has_exif",
        "exif_datetime",
        "camera_make",
        "camera_model",
        "software",
        "orientation",
        "error_message"
    ]

    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    return csv_path, json_path
