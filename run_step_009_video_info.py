from modules.video_info_extractor import extract_batch_video_info, export_video_info


def main():
    print("=" * 70)
    print("VIDEO-EXTRACT-009 | Video basic info and preview frames")
    print("=" * 70)

    results = extract_batch_video_info(
        input_folder="input_media",
        output_folder="output"
    )

    csv_path, json_path = export_video_info(results, "output")

    readable_count = sum(1 for item in results if item["is_readable"])
    unreadable_count = sum(1 for item in results if not item["is_readable"])
    total_preview_frames = sum(item.get("preview_frame_count", 0) for item in results)

    print(f"Videos found: {len(results)}")
    print(f"Readable videos: {readable_count}")
    print(f"Unreadable videos: {unreadable_count}")
    print(f"Preview frames generated: {total_preview_frames}")
    print(f"CSV report: {csv_path}")
    print(f"JSON report: {json_path}")
    print(f"Preview frame folder: output\\video_frames")

    if len(results) == 0:
        print("")
        print("Next action:")
        print("Put video files into input_media, then run this script again.")
    else:
        print("")
        print("Video extraction summary:")
        for item in results:
            status = "OK" if item["is_readable"] else "FAILED"
            dimension = f"{item['width']}x{item['height']}" if item["is_readable"] else ""
            duration = item.get("duration_hms", "")
            fps = item.get("fps", "")
            preview_count = item.get("preview_frame_count", 0)

            print(f"- {status} | {item['file_name']} | {dimension} | {duration} | fps: {fps} | frames: {preview_count}")

            if not item["is_readable"]:
                print(f"  ERROR: {item.get('error_message', '')}")

    print("")
    print("Step 9 completed.")


if __name__ == "__main__":
    main()
