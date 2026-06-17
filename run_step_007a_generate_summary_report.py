from pathlib import Path
import argparse
import win32com.client

from modules.local_ai_summary_report_generator import generate_local_summary_word_report


def convert_docx_to_pdf(docx_path, pdf_path):
    docx_file = Path(docx_path).resolve()
    pdf_file = Path(pdf_path).resolve()

    if not docx_file.exists():
        raise FileNotFoundError(f"Word report not found: {docx_file}")

    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False

    try:
        doc = word.Documents.Open(str(docx_file))
        doc.SaveAs(str(pdf_file), FileFormat=17)
        doc.Close()
    finally:
        word.Quit()

    return pdf_file


def normalize_format(value):
    value = (value or "").strip().lower()

    if value in ["1", "word", "docx"]:
        return "word"

    if value in ["2", "pdf"]:
        return "pdf"

    if value in ["3", "both", "all", "word+pdf"]:
        return "both"

    return "both"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--format",
        default="",
        help="Choose output format: word, pdf, or both"
    )
    args = parser.parse_args()

    print("=" * 80)
    print("VIDEO-EXTRACT-007A-Report V2 | Generate selectable report")
    print("=" * 80)

    report_format = normalize_format(args.format)

    if not args.format:
        print("")
        print("Choose report format:")
        print("1 = Word only")
        print("2 = PDF only")
        print("3 = Word + PDF")
        user_choice = input("Your choice: ")
        report_format = normalize_format(user_choice)

    reports_dir = Path("output/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    docx_path = reports_dir / "image_ai_summary_local_report.docx"
    pdf_path = reports_dir / "image_ai_summary_local_report.pdf"

    generated_word = None
    generated_pdf = None

    if report_format in ["word", "both", "pdf"]:
        generated_word = generate_local_summary_word_report(
            summary_json="output/image_ai_summary_local.json",
            basic_json="output/image_basic_info.json",
            output_docx=str(docx_path)
        )
        print(f"Word report generated: {generated_word}")

    if report_format in ["pdf", "both"]:
        try:
            generated_pdf = convert_docx_to_pdf(
                generated_word,
                str(pdf_path)
            )
            print(f"PDF report generated: {generated_pdf}")

            if report_format == "pdf":
                try:
                    Path(generated_word).unlink()
                    print("Temporary Word report removed because PDF-only mode was selected.")
                except Exception:
                    print("Temporary Word report could not be removed. You can delete it manually.")

        except Exception as e:
            print("PDF conversion failed.")
            print(f"Error: {e}")
            print("You can still open the Word report if it exists.")

    print("")
    print(f"Selected format: {report_format}")
    print(f"Reports folder: {reports_dir.resolve()}")
    print("Step 7A-Report V2 completed.")


if __name__ == "__main__":
    main()
