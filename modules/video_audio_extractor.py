from pathlib import Path
import csv
import json
import subprocess
from datetime import datetime

import imageio_ffmpeg


VIDEO_EXTENSIONS = {
    ".mp4", ".mov", ".avi", ".mkv", ".webm", ".flv", ".wmv", ".m4v", ".mpeg", ".mpg", ".3gp", ".ts"
}


def get_ffmpeg_exe():
    return imageio_ffmpeg.get_ffmpeg_exe()


def load_video_basic_info(json_path="output/video_basic_info.json"):
    path = Path(json_path)

    if not path.exists():
        return {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            items = json.load(f)

        return {item.get("file_name", ""): item for item in items}

    except Exception:
        return {}


def extract_audio_from_video(video_path: Path, output_audio_path: Path):
    ffmpeg_exe = get_ffmpeg_exe()
    output_audio_path.parent.mkdir(parents=True, exist_ok=True)

    command = [
        ffmpeg_exe,
        "-y",
        "-i", str(video_path),
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        str(output_audio_path)
    ]

    process = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore"
    )

    success = process.returncode == 0 and output_audio_path.exists()

    log_text = ""

    if process.stdout:
        log_text += process.stdout

    if process.stderr:
        log_text += process.stderr

    return success, log_text


def extract_batch_video_audio(input_folder="input_media", output_folder="output"):
    input_dir = Path(input_folder)
    output_dir = Path(output_folder)

    audio_root = output_dir / "video_audio"
    audio_root.mkdir(parents=True, exist_ok=True)

    video_info_lookup = load_video_basic_info(output_dir / "video_basic_info.json")

    results = []

    for video_path in input_dir.rglob("*"):
        if not video_path.is_file():
            continue

        if video_path.suffix.lower() not in VIDEO_EXTENSIONS:
            continue

        stat = video_path.stat()
        video_stem = video_path.stem

        video_audio_dir = audio_root / video_stem
        audio_path = video_audio_dir / f"{video_stem}_audio_16k_mono.wav"

        video_basic = video_info_lookup.get(video_path.name, {})

        result = {
            "file_name": video_path.name,
            "relative_path": str(video_path.relative_to(input_dir)),
            "full_path": str(video_path.resolve()),
            "extension": video_path.suffix.lower(),
            "video_size_mb": round(stat.st_size / (1024 * 1024), 3),
            "video_duration_hms": video_basic.get("duration_hms", ""),
            "video_duration_seconds": video_basic.get("duration_seconds", ""),
            "audio_extracted": False,
            "audio_path": "",
            "audio_size_mb": "",
            "audio_format": "wav",
            "audio_sample_rate": "16000",
            "audio_channels": "1",
            "whisper_ready": False,
            "modified_time": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            "error_message": "",
            "ffmpeg_log_preview": ""
        }

        try:
            success, log_text = extract_audio_from_video(video_path, audio_path)

            result["audio_extracted"] = success
            result["ffmpeg_log_preview"] = log_text[-500:]

            if success:
                result["audio_path"] = str(audio_path.resolve())
                result["audio_size_mb"] = round(audio_path.stat().st_size / (1024 * 1024), 3)
                result["whisper_ready"] = True
            else:
                result["error_message"] = "Audio extraction failed. The video may not contain an audio track or ffmpeg could not decode it."

        except Exception as e:
            result["error_message"] = str(e)

        results.append(result)

    return results


def export_audio_results(results, output_folder="output"):
    output_dir = Path(output_folder)
    output_dir.mkdir(exist_ok=True)

    csv_path = output_dir / "video_audio_info.csv"
    json_path = output_dir / "video_audio_info.json"
    queue_path = output_dir / "video_transcription_queue.json"

    fieldnames = [
        "file_name",
        "relative_path",
        "full_path",
        "extension",
        "video_size_mb",
        "video_duration_hms",
        "video_duration_seconds",
        "audio_extracted",
        "audio_path",
        "audio_size_mb",
        "audio_format",
        "audio_sample_rate",
        "audio_channels",
        "whisper_ready",
        "modified_time",
        "error_message",
        "ffmpeg_log_preview"
    ]

    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    queue_items = []

    for item in results:
        if item.get("whisper_ready") and item.get("audio_path"):
            queue_items.append({
                "file_name": item.get("file_name", ""),
                "audio_path": item.get("audio_path", ""),
                "language_hint": "auto",
                "status": "ready_for_whisper",
                "transcript_output": f"output/video_transcripts/{Path(item.get('file_name', '')).stem}_transcript.txt"
            })

    with open(queue_path, "w", encoding="utf-8") as f:
        json.dump(queue_items, f, ensure_ascii=False, indent=2)

    return csv_path, json_path, queue_path
