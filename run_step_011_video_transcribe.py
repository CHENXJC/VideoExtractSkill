from modules.video_transcriber import run_batch_video_transcription, export_transcription_results


def main():
    print("=" * 80)
    print("VIDEO-EXTRACT-011 | Local Whisper video speech-to-text transcription")
    print("=" * 80)

    results = run_batch_video_transcription(
        queue_path="output/video_transcription_queue.json",
        output_folder="output/video_transcripts",
        model_size="tiny"
    )

    csv_path, json_path = export_transcription_results(results, "output")

    total_files = len(results)
    success_count = sum(1 for item in results if item["transcription_success"])
    failed_count = total_files - success_count
    text_found_count = sum(1 for item in results if item["text_length"] > 0)

    print("")
    print("Transcription summary:")
    print(f"Audio files processed: {total_files}")
    print(f"Transcription success: {success_count}")
    print(f"Transcription failed: {failed_count}")
    print(f"Files with text found: {text_found_count}")
    print(f"CSV report: {csv_path}")
    print(f"JSON report: {json_path}")
    print(f"Transcript folder: output\\video_transcripts")

    print("")
    print("Transcript preview:")
    for item in results:
        status = "OK" if item["transcription_success"] else "FAILED"
        preview = item.get("transcript_text", "").replace("\n", " ")[:120]
        print(f"- {status} | {item['file_name']} | lang: {item.get('detected_language', '')} | length: {item.get('text_length', 0)}")
        if preview:
            print(f"  {preview}")
        if not item["transcription_success"]:
            print(f"  ERROR: {item.get('error_message', '')}")

    print("")
    print("Step 11 completed.")


if __name__ == "__main__":
    main()
