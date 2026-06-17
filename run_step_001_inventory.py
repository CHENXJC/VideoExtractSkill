from modules.file_scanner import scan_media_folder, export_inventory


def main():
    print("=" * 60)
    print("VIDEO-EXTRACT-001 | Step 1: Batch media inventory scan")
    print("=" * 60)

    results = scan_media_folder("input_media")
    csv_path, json_path = export_inventory(results, "output")

    print(f"Scanned files: {len(results)}")
    print(f"CSV report: {csv_path}")
    print(f"JSON report: {json_path}")

    if len(results) == 0:
        print("")
        print("Next action:")
        print("Put some videos/images into the input_media folder, then run this script again.")
    else:
        print("")
        print("File type summary:")
        summary = {}
        for item in results:
            summary[item["file_type"]] = summary.get(item["file_type"], 0) + 1

        for file_type, count in summary.items():
            print(f"- {file_type}: {count}")

    print("")
    print("Step 1 completed.")


if __name__ == "__main__":
    main()
