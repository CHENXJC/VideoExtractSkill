from modules.local_ai_summarizer import run_local_ai_summary


def main():
    print("=" * 70)
    print("VIDEO-EXTRACT-007A | Local rule-based AI summary")
    print("=" * 70)

    results, json_path, csv_path, txt_dir = run_local_ai_summary(
        input_json="output/image_ocr_results_cleaned.json",
        output_folder="output"
    )

    print(f"Files analyzed: {len(results)}")
    print(f"JSON output: {json_path}")
    print(f"CSV output : {csv_path}")
    print(f"TXT folder : {txt_dir}")
    print("")

    print("Summary preview:")
    for item in results:
        keywords = "、".join(item.get("keywords", [])[:5])
        summary = item.get("summary", "").replace("\n", " ")[:120]
        print(f"- {item['file_name']} | {item['content_type']} | {keywords}")
        print(f"  {summary}")

    print("")
    print("Step 7A completed.")


if __name__ == "__main__":
    main()
