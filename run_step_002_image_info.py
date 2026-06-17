from modules.image_info_extractor import extract_batch_image_info, export_image_info


def main():
    print("=" * 70)
    print("VIDEO-EXTRACT-002 | Batch image basic information extractor")
    print("=" * 70)

    results = extract_batch_image_info("input_media")
    csv_path, json_path = export_image_info(results, "output")

    readable_count = sum(1 for item in results if item["is_readable"])
    unreadable_count = sum(1 for item in results if not item["is_readable"])

    print(f"Images found: {len(results)}")
    print(f"Readable images: {readable_count}")
    print(f"Unreadable images: {unreadable_count}")
    print(f"CSV report: {csv_path}")
    print(f"JSON report: {json_path}")

    if len(results) == 0:
        print("")
        print("Next action:")
        print("Put some image files into input_media, then run this script again.")
    else:
        print("")
        print("Image extraction summary:")
        for item in results:
            status = "OK" if item["is_readable"] else "FAILED"
            print(f"- {status} | {item['file_name']} | {item['width']}x{item['height']} | {item['image_format']}")

    print("")
    print("Step 2 completed.")


if __name__ == "__main__":
    main()
