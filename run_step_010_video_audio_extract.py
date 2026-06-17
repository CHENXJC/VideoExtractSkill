from modules.video_audio_extractor import extract_batch_video_audio, export_audio_results


def main():
    print("=" * 80)
    print("VIDEO-EXTRACT-010 | Video audio extraction and Whisper preparation")
    print("=" * 80)

    results = extract_batch_video_audio(
        input_folder="input_media",
        output_folder="output"
    )

    csv_path, json_path, queue_path = export_audio_results(results, "output")

    total_videos = len(results)
    extracted_count = sum(1 for item in results if item["audio_extracted"])
    failed_count = total_videos - extracted_count
    whisper_ready_count = sum(1 for item in results if item["whisper_ready"])

    print(f"Videos found: {total_videos}")
    print(f"Audio extracted: {extracted_count}")
    print(f"Audio failed: {failed_count}")
    print(f"Whisper ready files: {whisper_ready_count}")
    print(f"CSV report: {csv_path}")
    print(f"JSON report: {json_path}")
    print(f"Whisper queue: {queue_path}")
    print(f"Audio folder: output\\video_audio")

    if total_videos == 0:
        print("")
        print("Next action:")
        print("Put video files into input_media, then run this script again.")
    else:
        print("")
        print("Audio extraction summary:")

        for item in results:
            status = "OK" if item["audio_extracted"] else "FAILED"
            audio_size = item.get("audio_size_mb", "")
            duration = item.get("video_duration_hms", "")

            print(f"- {status} | {item['file_name']} | duration: {duration} | audio size: {audio_size} MB")

            if not item["audio_extracted"]:
                print(f"  ERROR: {item.get('error_message', '')}")

    print("")
    print("Step 10 completed.")


if __name__ == "__main__":
    main()
