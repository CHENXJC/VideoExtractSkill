from modules.ocr_text_formatter import process_ocr_json


def main():
    print("=" * 70)
    print("VIDEO-EXTRACT-005D | OCR text cleanup and formatting")
    print("=" * 70)

    results, json_path, csv_path, txt_dir = process_ocr_json(
        input_json="output/image_ocr_results.json",
        output_folder="output"
    )

    print(f"Files processed: {len(results)}")
    print(f"Cleaned JSON: {json_path}")
    print(f"Cleaned CSV : {csv_path}")
    print(f"Cleaned TXT folder: {txt_dir}")
    print("")

    print("Preview:")
    for item in results:
        preview = item.get("cleaned_text", "").replace("\n", " ")[:120]
        print(f"- {item['file_name']} | cleaned length: {item.get('cleaned_text_length', 0)} | {preview}")

    print("")
    print("Step 5D completed.")


if __name__ == "__main__":
    main()
