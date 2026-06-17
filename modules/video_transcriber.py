from pathlib import Path
import json
import csv
from datetime import datetime

from faster_whisper import WhisperModel


def load_transcription_queue(queue_path="output/video_transcription_queue.json"):
    path = Path(queue_path)

    if not path.exists():
        raise FileNotFoundError(
            "video_transcription_queue.json not found. Please run Step 10 first."
        )

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def ensure_output_folder(output_folder="output/video_transcripts"):
    path = Path(output_folder)
    path.mkdir(parents=True, exist_ok=True)
    return path


def transcribe_single_audio(model, queue_item, output_folder):
    audio_path = Path(queue_item.get("audio_path", ""))
    file_name = queue_item.get("file_name", audio_path.name)

    result = {
        "file_name": file_name,
        "audio_path": str(audio_path),
        "transcription_success": False,
        "detected_language": "",
        "language_probability": "",
        "text_length": 0,
        "transcript_text": "",
        "segments_count": 0,
        "txt_output": "",
        "json_output": "",
        "processed_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "error_message": ""
    }

    if not audio_path.exists():
        result["error_message"] = f"Audio file not found: {audio_path}"
        return result

    try:
        segments, info = model.transcribe(
            str(audio_path),
            beam_size=5,
            vad_filter=True
        )

        segment_items = []
        transcript_parts = []

        for segment in segments:
            segment_text = segment.text.strip()

            segment_items.append({
                "start": round(segment.start, 3),
                "end": round(segment.end, 3),
                "text": segment_text
            })

            if segment_text:
                transcript_parts.append(segment_text)

        transcript_text = "\n".join(transcript_parts).strip()

        safe_stem = Path(file_name).stem
        txt_path = Path(output_folder) / f"{safe_stem}_transcript.txt"
        json_path = Path(output_folder) / f"{safe_stem}_transcript.json"

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(transcript_text)

        transcript_json = {
            "file_name": file_name,
            "audio_path": str(audio_path),
            "detected_language": getattr(info, "language", ""),
            "language_probability": round(float(getattr(info, "language_probability", 0)), 4),
            "duration": round(float(getattr(info, "duration", 0)), 3),
            "segments": segment_items,
            "transcript_text": transcript_text
        }

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(transcript_json, f, ensure_ascii=False, indent=2)

        result["transcription_success"] = True
        result["detected_language"] = transcript_json["detected_language"]
        result["language_probability"] = transcript_json["language_probability"]
        result["text_length"] = len(transcript_text)
        result["transcript_text"] = transcript_text
        result["segments_count"] = len(segment_items)
        result["txt_output"] = str(txt_path.resolve())
        result["json_output"] = str(json_path.resolve())

    except Exception as e:
        result["error_message"] = str(e)

    return result


def run_batch_video_transcription(
    queue_path="output/video_transcription_queue.json",
    output_folder="output/video_transcripts",
    model_size="tiny"
):
    queue_items = load_transcription_queue(queue_path)
    transcript_dir = ensure_output_folder(output_folder)

    print(f"Loading Whisper model: {model_size}")
    print("First run may take several minutes because the model needs to be downloaded.")
    print("")

    model = WhisperModel(
        model_size,
        device="cpu",
        compute_type="int8"
    )

    results = []

    for index, item in enumerate(queue_items, start=1):
        print(f"[{index}/{len(queue_items)}] Transcribing: {item.get('file_name', '')}")
        result = transcribe_single_audio(
            model=model,
            queue_item=item,
            output_folder=transcript_dir
        )
        results.append(result)

        if result["transcription_success"]:
            print(f"  OK | language: {result['detected_language']} | text length: {result['text_length']}")
        else:
            print(f"  FAILED | {result['error_message']}")

    return results


def export_transcription_results(results, output_folder="output"):
    output_dir = Path(output_folder)
    output_dir.mkdir(exist_ok=True)

    csv_path = output_dir / "video_transcription_results.csv"
    json_path = output_dir / "video_transcription_results.json"

    fieldnames = [
        "file_name",
        "audio_path",
        "transcription_success",
        "detected_language",
        "language_probability",
        "text_length",
        "segments_count",
        "txt_output",
        "json_output",
        "processed_time",
        "error_message",
        "transcript_text"
    ]

    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    return csv_path, json_path
