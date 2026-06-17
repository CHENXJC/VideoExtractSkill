from pathlib import Path
import os
import json
import csv
from datetime import datetime

from openai import OpenAI


DEFAULT_MODEL = os.getenv("OPENAI_SUMMARY_MODEL", "gpt-5.5")


def get_openai_client():
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Please set it as a Windows environment variable first."
        )

    return OpenAI()


def load_json_if_exists(path):
    file_path = Path(path)

    if not file_path.exists():
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def collect_media_text_items():
    items = []

    image_items = load_json_if_exists("output/image_ocr_results_cleaned.json")

    for item in image_items:
        text = item.get("cleaned_text") or item.get("extracted_text") or ""

        if text.strip():
            items.append({
                "media_type": "image",
                "file_name": item.get("file_name", ""),
                "language": item.get("ocr_language", ""),
                "source_text": text.strip()
            })

    video_items = load_json_if_exists("output/video_summary_local.json")

    for item in video_items:
        text = item.get("cleaned_text") or item.get("source_transcript") or ""

        if text.strip():
            items.append({
                "media_type": "video",
                "file_name": item.get("file_name", ""),
                "language": item.get("detected_language", ""),
                "source_text": text.strip()
            })

    return items


def safe_json_parse(text):
    text = text.strip()

    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(text)
    except Exception:
        return {
            "summary": text[:800],
            "keywords": [],
            "key_points": [],
            "content_type": "Unknown",
            "action_suggestions": [],
            "archive_suggestion": "",
            "reuse_ideas": [],
            "risk_notes": [],
            "raw_model_output": text
        }


def build_prompt(item):
    source_text = item["source_text"]

    if len(source_text) > 8000:
        source_text = source_text[:8000]

    return f"""
You are an expert media information analyst.

Analyze the following OCR/transcript text extracted from a media file.

File name: {item['file_name']}
Media type: {item['media_type']}
Detected language: {item.get('language', '')}

Text:
{source_text}

Return ONLY valid JSON in this exact structure:
{{
  "summary": "A clear, natural summary in Chinese.",
  "keywords": ["keyword1", "keyword2", "keyword3"],
  "key_points": ["point1", "point2", "point3"],
  "content_type": "One clear category, such as AI prompt, learning material, sales script, business analysis, social media content, technical tutorial, etc.",
  "action_suggestions": ["suggestion1", "suggestion2", "suggestion3"],
  "archive_suggestion": "Where this file should be archived.",
  "reuse_ideas": ["how this content can be reused 1", "how this content can be reused 2"],
  "risk_notes": ["possible issue or limitation 1"]
}}
"""


def analyze_item_with_openai(client, item, model=DEFAULT_MODEL):
    prompt = build_prompt(item)

    response = client.responses.create(
        model=model,
        input=prompt,
    )

    output_text = response.output_text
    parsed = safe_json_parse(output_text)

    result = {
        "file_name": item["file_name"],
        "media_type": item["media_type"],
        "language": item.get("language", ""),
        "model": model,
        "processed_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source_text_length": len(item.get("source_text", "")),
        "summary": parsed.get("summary", ""),
        "keywords": parsed.get("keywords", []),
        "key_points": parsed.get("key_points", []),
        "content_type": parsed.get("content_type", ""),
        "action_suggestions": parsed.get("action_suggestions", []),
        "archive_suggestion": parsed.get("archive_suggestion", ""),
        "reuse_ideas": parsed.get("reuse_ideas", []),
        "risk_notes": parsed.get("risk_notes", []),
        "raw_model_output": parsed.get("raw_model_output", "")
    }

    return result


def run_openai_enhanced_summary(model=DEFAULT_MODEL):
    client = get_openai_client()
    items = collect_media_text_items()

    results = []

    for index, item in enumerate(items, start=1):
        print(f"[{index}/{len(items)}] Analyzing {item['media_type']}: {item['file_name']}")

        try:
            result = analyze_item_with_openai(client, item, model=model)
            results.append(result)
            print(f"  OK | {result.get('content_type', '')} | {result.get('summary', '')[:80]}")
        except Exception as e:
            results.append({
                "file_name": item["file_name"],
                "media_type": item["media_type"],
                "language": item.get("language", ""),
                "model": model,
                "processed_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "source_text_length": len(item.get("source_text", "")),
                "summary": "",
                "keywords": [],
                "key_points": [],
                "content_type": "",
                "action_suggestions": [],
                "archive_suggestion": "",
                "reuse_ideas": [],
                "risk_notes": [],
                "raw_model_output": "",
                "error_message": str(e)
            })
            print(f"  FAILED | {e}")

    return results


def export_openai_summary_results(results, output_folder="output"):
    output_dir = Path(output_folder)
    output_dir.mkdir(exist_ok=True)

    txt_dir = output_dir / "openai_enhanced_summaries"
    txt_dir.mkdir(exist_ok=True)

    json_path = output_dir / "openai_enhanced_summary.json"
    csv_path = output_dir / "openai_enhanced_summary.csv"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    fieldnames = [
        "file_name",
        "media_type",
        "language",
        "model",
        "processed_time",
        "source_text_length",
        "content_type",
        "summary",
        "keywords",
        "key_points",
        "action_suggestions",
        "archive_suggestion",
        "reuse_ideas",
        "risk_notes",
        "error_message"
    ]

    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for item in results:
            row = dict(item)
            row["keywords"] = " | ".join(item.get("keywords", []))
            row["key_points"] = " | ".join(item.get("key_points", []))
            row["action_suggestions"] = " | ".join(item.get("action_suggestions", []))
            row["reuse_ideas"] = " | ".join(item.get("reuse_ideas", []))
            row["risk_notes"] = " | ".join(item.get("risk_notes", []))
            writer.writerow({k: row.get(k, "") for k in fieldnames})

    for item in results:
        safe_name = Path(item["file_name"]).stem
        txt_path = txt_dir / f"{safe_name}_{item['media_type']}_openai_summary.txt"

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(f"File: {item.get('file_name', '')}\n")
            f.write(f"Media Type: {item.get('media_type', '')}\n")
            f.write(f"Content Type: {item.get('content_type', '')}\n")
            f.write(f"Model: {item.get('model', '')}\n\n")

            f.write("Summary:\n")
            f.write(item.get("summary", "") + "\n\n")

            f.write("Keywords:\n")
            f.write("、".join(item.get("keywords", [])) + "\n\n")

            f.write("Key Points:\n")
            for i, point in enumerate(item.get("key_points", []), start=1):
                f.write(f"{i}. {point}\n")

            f.write("\nAction Suggestions:\n")
            for i, suggestion in enumerate(item.get("action_suggestions", []), start=1):
                f.write(f"{i}. {suggestion}\n")

            f.write("\nArchive Suggestion:\n")
            f.write(item.get("archive_suggestion", "") + "\n\n")

            f.write("Reuse Ideas:\n")
            for i, idea in enumerate(item.get("reuse_ideas", []), start=1):
                f.write(f"{i}. {idea}\n")

            f.write("\nRisk Notes:\n")
            for i, note in enumerate(item.get("risk_notes", []), start=1):
                f.write(f"{i}. {note}\n")

            if item.get("error_message"):
                f.write("\nError:\n")
                f.write(item.get("error_message", ""))

    return json_path, csv_path, txt_dir
