from pathlib import Path
import csv
import json
import re


def is_mostly_chinese(text: str) -> bool:
    chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
    visible_chars = re.findall(r'[\u4e00-\u9fffA-Za-z0-9]', text)
    if not visible_chars:
        return False
    return len(chinese_chars) / max(len(visible_chars), 1) > 0.35


def clean_line_basic(line: str) -> str:
    line = line.replace("\u3000", " ")
    line = re.sub(r"[ \t]+", " ", line)
    line = line.strip()
    return line


def merge_broken_chinese_spacing(text: str) -> str:
    # 去掉中文字符之间多余空格
    text = re.sub(r'(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])', '', text)
    # 去掉中文和中文标点之间多余空格
    text = re.sub(r'(?<=[\u4e00-\u9fff])\s+(?=[，。！？：；、“”‘’（）《》【】])', '', text)
    text = re.sub(r'(?<=[，。！？：；、“”‘’（）《》【】])\s+(?=[\u4e00-\u9fff])', '', text)
    return text


def normalize_punctuation_spacing(text: str) -> str:
    # 英文标点后保留一个空格（如果后面是英文/数字）
    text = re.sub(r'([,:;])([A-Za-z0-9])', r'\1 \2', text)
    # 中文冒号等不需要前后多余空格
    text = re.sub(r'\s*([，。！？：；])\s*', r'\1', text)
    return text


def looks_like_heading(line: str) -> bool:
    if len(line) <= 20 and not line.endswith(("。", "，", ".", ",")):
        return True
    if re.match(r'^\d+[\.、]\s*', line):
        return True
    if re.match(r'^[一二三四五六七八九十]+[、\.]\s*', line):
        return True
    if any(keyword in line for keyword in ["任务目标", "视觉规范", "构图布局", "Image Preview", "Report Summary"]):
        return True
    return False


def looks_like_bullet(line: str) -> bool:
    return bool(re.match(r'^[-•·▪◦*]\s*', line))


def smart_join_lines(lines):
    paragraphs = []
    current = ""

    for raw_line in lines:
        line = clean_line_basic(raw_line)

        if not line:
            if current.strip():
                paragraphs.append(current.strip())
                current = ""
            continue

        if looks_like_heading(line):
            if current.strip():
                paragraphs.append(current.strip())
            paragraphs.append(line)
            current = ""
            continue

        if looks_like_bullet(line):
            if current.strip():
                paragraphs.append(current.strip())
                current = ""
            paragraphs.append(line)
            continue

        if not current:
            current = line
        else:
            # 如果当前段落和新行都偏中文，就直接拼接
            if is_mostly_chinese(current + line):
                current += line
            else:
                # 英文/混合内容之间加空格
                current += " " + line

    if current.strip():
        paragraphs.append(current.strip())

    return paragraphs


def final_cleanup(paragraphs):
    cleaned = []

    for p in paragraphs:
        p = merge_broken_chinese_spacing(p)
        p = normalize_punctuation_spacing(p)

        # 某些 OCR 会把项目符号和正文粘一起，做一点温和修复
        p = re.sub(r'^-\s*', '- ', p)
        p = re.sub(r'^\*\s*', '* ', p)

        cleaned.append(p.strip())

    return cleaned


def format_clean_text(raw_text: str) -> str:
    raw_text = raw_text.replace("\r\n", "\n").replace("\r", "\n")
    raw_text = raw_text.strip()

    if not raw_text:
        return ""

    lines = raw_text.split("\n")
    paragraphs = smart_join_lines(lines)
    paragraphs = final_cleanup(paragraphs)

    return "\n\n".join(paragraphs).strip()


def process_ocr_json(input_json="output/image_ocr_results.json", output_folder="output"):
    input_path = Path(input_json)
    output_dir = Path(output_folder)
    output_dir.mkdir(exist_ok=True)

    cleaned_txt_dir = output_dir / "ocr_texts_cleaned"
    cleaned_txt_dir.mkdir(exist_ok=True)

    cleaned_json_path = output_dir / "image_ocr_results_cleaned.json"
    cleaned_csv_path = output_dir / "image_ocr_results_cleaned.csv"

    if not input_path.exists():
        raise FileNotFoundError("image_ocr_results.json not found. Please run OCR first.")

    with open(input_path, "r", encoding="utf-8") as f:
        results = json.load(f)

    cleaned_results = []

    for item in results:
        raw_text = item.get("extracted_text", "")
        cleaned_text = format_clean_text(raw_text)

        new_item = dict(item)
        new_item["cleaned_text"] = cleaned_text
        new_item["cleaned_text_length"] = len(cleaned_text)

        cleaned_results.append(new_item)

        safe_name = Path(item["file_name"]).stem
        txt_path = cleaned_txt_dir / f"{safe_name}_ocr_cleaned.txt"
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(cleaned_text)

    with open(cleaned_json_path, "w", encoding="utf-8") as f:
        json.dump(cleaned_results, f, ensure_ascii=False, indent=2)

    fieldnames = [
        "file_name",
        "ocr_language",
        "ocr_success",
        "text_length",
        "cleaned_text_length",
        "extracted_text",
        "cleaned_text",
        "error_message"
    ]

    with open(cleaned_csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for item in cleaned_results:
            row = {k: item.get(k, "") for k in fieldnames}
            writer.writerow(row)

    return cleaned_results, cleaned_json_path, cleaned_csv_path, cleaned_txt_dir
