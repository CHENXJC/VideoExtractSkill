from modules.video_summary_local import run_video_summary
from modules.video_summary_report_generator import generate_video_summary_report


def main():
    print("=" * 80)
    print("VIDEO-EXTRACT-012 | Video transcript cleanup and summary report")
    print("=" * 80)

    results, json_path, csv_path, txt_dir = run_video_summary(
        input_json="output/video_transcription_results.json",
        output_folder="output"
    )

    print(f"Videos summarized: {len(results)}")
    print(f"JSON output: {json_path}")
    print(f"CSV output: {csv_path}")
    print(f"TXT folder: {txt_dir}")

    docx_path, pdf_path = generate_video_summary_report(
        summary_json="output/video_summary_local.json",
        output_docx="output/reports/video_summary_local_report.docx",
        output_pdf="output/reports/video_summary_local_report.pdf",
        report_format="both"
    )

    print("")
    if docx_path:
        print(f"Word report generated: {docx_path}")
    if pdf_path:
        print(f"PDF report generated: {pdf_path}")

    print("")
    print("Summary preview:")
    for item in results:
        keywords = "、".join(item.get("keywords", [])[:6])
        summary = item.get("summary", "").replace("\n", " ")[:160]
        print(f"- {item['file_name']} | {item['content_type']} | {keywords}")
        print(f"  {summary}")

    print("")
    print("Step 12 completed.")


if __name__ == "__main__":
    main()
