from modules.image_ocr_extractor import extract_batch_image_ocr, export_ocr_results


def main():
    print("=" * 70)
    print("VIDEO-EXTRACT-005 | Batch image OCR text extraction")
    print("=" * 70)

    try:
        results, tesseract_path, available_languages, selected_language = extract_batch_image_ocr("input_media")
        csv_path, json_path, text_dir = export_ocr_results(results, "output")

        success_count = sum(1 for item in results if item["ocr_success"])
        failed_count = sum(1 for item in results if not item["ocr_success"])
        text_found_count = sum(1 for item in results if item["text_length"] > 0)

        print(f"Tesseract path: {tesseract_path}")
        print(f"Available languages: {available_languages}")
        print(f"Selected OCR language: {selected_language}")
        print("")
        print(f"Images processed: {len(results)}")
        print(f"OCR success: {success_count}")
        print(f"OCR failed: {failed_count}")
        print(f"Images with text found: {text_found_count}")
        print(f"CSV report: {csv_path}")
        print(f"JSON report: {json_path}")
        print(f"TXT folder: {text_dir}")

        print("")
        print("OCR summary:")
        for item in results:
            status = "OK" if item["ocr_success"] else "FAILED"
            preview = item["extracted_text"].replace("\n", " ")[:80]
            print(f"- {status} | {item['file_name']} | lang: {item['ocr_language']} | text length: {item['text_length']} | {preview}")

            if not item["ocr_success"]:
                print(f"  ERROR: {item['error_message'][:300]}")

        print("")
        print("Step 5 completed.")

    except RuntimeError as e:
        print("")
        print("OCR environment is not ready.")
        print(f"Reason: {e}")


if __name__ == "__main__":
    main()
