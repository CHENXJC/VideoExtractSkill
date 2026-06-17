from pathlib import Path
import csv
import json
import shutil
import subprocess
import os
from datetime import datetime

from PIL import Image, ImageOps
import pytesseract


COMMON_TESSERACT_PATHS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
]

PROJECT_TESSDATA_DIR = Path("tessdata").resolve()
PROJECT_TESSDATA_DIR_FOR_TESSERACT = str(PROJECT_TESSDATA_DIR).replace("\\", "/")

IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".tiff", ".tif", ".heic", ".heif", ".avif"
}


def find_tesseract():
    found = shutil.which("tesseract")

    if found:
        return found

    for path in COMMON_TESSERACT_PATHS:
        if Path(path).exists():
            return path

    return None


def configure_tesseract():
    tesseract_path = find_tesseract()

    if not tesseract_path:
        return False, ""

    pytesseract.pytesseract.tesseract_cmd = tesseract_path

    # Important: tell Tesseract where the local language files are.
    os.environ["TESSDATA_PREFIX"] = str(PROJECT_TESSDATA_DIR)

    return True, tesseract_path


def get_available_languages():
    try:
        result = subprocess.run(
            [
                pytesseract.pytesseract.tesseract_cmd,
                "--tessdata-dir",
                PROJECT_TESSDATA_DIR_FOR_TESSERACT,
                "--list-langs"
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )

        lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        languages = []

        for line in lines:
            if "List of available languages" in line:
                continue
            languages.append(line)

        return languages

    except Exception:
        return []


def build_language_try_list(available_languages):
    languages = []

    if "eng" in available_languages and "chi_sim" in available_languages:
        languages.append("eng+chi_sim")

    if "chi_sim" in available_languages:
        languages.append("chi_sim")

    if "eng" in available_languages:
        languages.append("eng")

    if not languages:
        languages.append("eng")

    return languages


def preprocess_image_for_ocr(image_path: Path):
    image = Image.open(image_path)
    image = ImageOps.exif_transpose(image)

    if image.mode not in ["RGB", "L"]:
        image = image.convert("RGB")

    image = image.convert("L")

    width, height = image.size

    if width < 1400:
        scale = 1400 / width
        new_height = int(height * scale)
        image = image.resize((1400, new_height))

    return image


def run_ocr_with_fallback(image, language_try_list):
    error_messages = []

    for language in language_try_list:
        try:
            # Do not put extra quotes around tessdata path.
            config = f"--tessdata-dir {PROJECT_TESSDATA_DIR_FOR_TESSERACT} --oem 1 --psm 6"

            text = pytesseract.image_to_string(
                image,
                lang=language,
                config=config
            )

            return True, language, text.strip(), ""

        except Exception as e:
            error_messages.append(f"[{language}] {str(e)}")

    return False, "", "", " | ".join(error_messages)


def extract_text_from_single_image(file_path: Path, root_folder: Path, language_try_list):
    stat = file_path.stat()

    result = {
        "file_name": file_path.name,
        "relative_path": str(file_path.relative_to(root_folder)),
        "full_path": str(file_path.resolve()),
        "extension": file_path.suffix.lower(),
        "size_mb": round(stat.st_size / (1024 * 1024), 3),
        "modified_time": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
        "ocr_language": "",
        "ocr_success": False,
        "text_length": 0,
        "extracted_text": "",
        "error_message": ""
    }

    try:
        image = preprocess_image_for_ocr(file_path)

        success, used_language, text, error_message = run_ocr_with_fallback(
            image=image,
            language_try_list=language_try_list
        )

        result["ocr_success"] = success
        result["ocr_language"] = used_language
        result["text_length"] = len(text)
        result["extracted_text"] = text
        result["error_message"] = error_message

    except Exception as e:
        result["error_message"] = str(e)

    return result


def extract_batch_image_ocr(input_folder: str = "input_media"):
    root_folder = Path(input_folder)
    results = []

    tesseract_ok, tesseract_path = configure_tesseract()

    if not tesseract_ok:
        raise RuntimeError(
            "Tesseract OCR was not found. Please install Tesseract OCR first."
        )

    available_languages = get_available_languages()
    language_try_list = build_language_try_list(available_languages)

    for file_path in root_folder.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in IMAGE_EXTENSIONS:
            results.append(
                extract_text_from_single_image(
                    file_path=file_path,
                    root_folder=root_folder,
                    language_try_list=language_try_list
                )
            )

    selected_language = "+fallback: " + " -> ".join(language_try_list)

    return results, tesseract_path, available_languages, selected_language


def export_ocr_results(results, output_folder: str = "output"):
    output_dir = Path(output_folder)
    output_dir.mkdir(exist_ok=True)

    text_dir = output_dir / "ocr_texts"
    text_dir.mkdir(exist_ok=True)

    csv_path = output_dir / "image_ocr_results.csv"
    json_path = output_dir / "image_ocr_results.json"

    fieldnames = [
        "file_name",
        "relative_path",
        "full_path",
        "extension",
        "size_mb",
        "modified_time",
        "ocr_language",
        "ocr_success",
        "text_length",
        "extracted_text",
        "error_message"
    ]

    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    for item in results:
        safe_name = Path(item["file_name"]).stem
        txt_path = text_dir / f"{safe_name}_ocr.txt"

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(item.get("extracted_text", ""))

    return csv_path, json_path, text_dir
