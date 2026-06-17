from pathlib import Path
import subprocess
import sys
import os
import json
import shutil
from datetime import datetime

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent
INPUT_DIR = PROJECT_ROOT / "input_media"
OUTPUT_DIR = PROJECT_ROOT / "output"
REPORTS_DIR = OUTPUT_DIR / "reports"
BATCHES_DIR = REPORTS_DIR / "batches"
VIDEO_FRAMES_DIR = OUTPUT_DIR / "video_frames"
VIDEO_TRANSCRIPTS_DIR = OUTPUT_DIR / "video_transcripts"

IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".tiff", ".tif", ".heic", ".heif", ".avif"
}

VIDEO_EXTENSIONS = {
    ".mp4", ".mov", ".avi", ".mkv", ".webm", ".flv", ".wmv", ".m4v", ".mpeg", ".mpg", ".3gp", ".ts"
}

THEMES = {
    "Ocean Blue": {
        "accent": "#0A84FF",
        "accent_soft": "#E8F3FF",
        "accent_2": "#5AC8FA",
        "glow": "rgba(10,132,255,0.18)",
        "hero_grad_1": "rgba(10,132,255,0.10)",
        "hero_grad_2": "rgba(90,200,250,0.10)",
        "badge_bg": "#EAF4FF",
        "badge_text": "#0A66D9",
        "button_text": "#FFFFFF",
    },
    "Lavender": {
        "accent": "#7C5CFF",
        "accent_soft": "#F0EBFF",
        "accent_2": "#B28DFF",
        "glow": "rgba(124,92,255,0.18)",
        "hero_grad_1": "rgba(124,92,255,0.10)",
        "hero_grad_2": "rgba(178,141,255,0.12)",
        "badge_bg": "#F1EDFF",
        "badge_text": "#6547E6",
        "button_text": "#FFFFFF",
    },
    "Sunset Coral": {
        "accent": "#FF6B57",
        "accent_soft": "#FFF0EC",
        "accent_2": "#FF9F7A",
        "glow": "rgba(255,107,87,0.18)",
        "hero_grad_1": "rgba(255,107,87,0.10)",
        "hero_grad_2": "rgba(255,159,122,0.12)",
        "badge_bg": "#FFF1EC",
        "badge_text": "#E25745",
        "button_text": "#FFFFFF",
    }
}


TEXT = {
    "zh": {
        "app_title": "Batch Media Insight Extractor",
        "app_subtitle": "批量图片与视频信息提取软件",
        "app_caption": "把图片和视频批量变成文字、摘要、关键词和 Word/PDF 报告。",
        "language": "语言",
        "theme": "主题颜色",
        "navigation": "导航",
        "dashboard": "首页 Dashboard",
        "upload": "上传文件",
        "files": "文件管理",
        "image_summary": "图片总结",
        "video_info": "视频信息",
        "video_transcript": "视频转文字",
        "reports": "报告中心",
        "settings": "设置",
        "workflow_history": "运行历史",
        "workflow_history_title": "运行历史与最新状态",
        "latest_run_status": "最近一次完整流程状态",
        "latest_log_file": "最新日志文件",
        "open_latest_log": "打开最新日志",
        "open_latest_status": "打开最新状态文件",
        "recent_logs": "最近日志记录",
        "recent_batches": "最近批次报告",
        "workflow_steps": "流程步骤记录",
        "settings_title": "设置与 Demo 模式",
        "demo_mode_title": "Demo 模式",
        "demo_mode_desc": "使用安全 demo 素材测试软件、生成展示截图和样例报告，不暴露私人文件。",
        "open_demo_assets": "打开 Demo 素材文件夹",
        "copy_demo_to_input": "复制 Demo 素材到 input_media",
        "clear_and_use_demo": "清空 input_media 并使用 Demo 素材",
        "confirm_clear_for_demo": "确认清空 input_media 并切换为 Demo 素材",
        "copied_demo": "Demo 素材已复制到 input_media，文件数量：",
        "no_demo_files": "没有找到 Demo 素材，请先运行 VIDEO-EXTRACT-023。",
        "latest_batch_report": "最新批次报告",
        "open_latest_batch": "打开最新批次报告",
        "no_batch_found": "没有找到批次报告。",
        "latest_demo_report": "最新 Demo 报告",
        "open_latest_demo_report": "打开最新 Demo 报告",
        "no_demo_report_found": "没有找到 Demo 报告。",
        "local_mode_note": "当前为本地模式：不消耗 OpenAI API credits。",
        "quality_note": "产品标准：稳定、清晰、安全、长期可用。",
        "project_folders": "项目文件夹",
        "project_folder": "项目路径",
        "input_folder": "输入文件夹",
        "reports_folder": "报告文件夹",
        "batch_folder": "批次报告",
        "video_frames_folder": "视频预览帧",
        "video_transcripts_folder": "视频转写",
        "open_input": "打开 input_media",
        "open_reports": "打开 reports",
        "open_batches": "打开 batches",
        "open_video_frames": "打开 video_frames",
        "open_video_transcripts": "打开 video_transcripts",
        "tools": "工具",
        "confirm_clear_input": "确认清空 input_media",
        "confirm_clear_reports": "确认清空 reports",
        "clear_input": "清空 input_media",
        "clear_reports": "清空 reports",
        "clear_input_success": "input_media 已清空。",
        "clear_reports_success": "reports 已清空。",
        "total_files": "总文件",
        "images": "图片",
        "videos": "视频",
        "reports_count": "报告",
        "main_actions": "主要功能",
        "local_full_workflow_title": "一键本地完整流程",
        "local_full_workflow_desc": "自动处理 input_media 中的图片和视频：图片 OCR、视频转文字、本地总结、Word/PDF 报告和批次归档。",
        "run_local_full": "一键运行本地完整流程",
        "image_workflow_title": "图片完整流程",
        "image_workflow_desc": "批量图片 OCR、文本清洗、本地 AI 总结，并生成 Word/PDF 报告。",
        "video_workflow_title": "视频转文字流程",
        "video_workflow_desc": "提取音频、Whisper 转文字、生成视频摘要与 Word/PDF 报告。",
        "video_info_title": "视频基础信息",
        "video_info_desc": "提取视频时长、分辨率、FPS，并自动生成预览帧。",
        "report_center_title": "报告中心",
        "report_center_desc": "查看、下载和管理已经生成的 Word/PDF 报告。",
        "choose_format": "选择图片报告格式",
        "word_only": "只生成 Word",
        "pdf_only": "只生成 PDF",
        "word_pdf": "Word + PDF",
        "create_batch": "生成独立批次文件夹",
        "run_image": "运行图片流程",
        "run_video": "运行视频转文字",
        "run_video_info": "提取视频信息",
        "open_report_center": "打开报告中心",
        "no_images": "没有找到图片文件。请先上传或放入图片。",
        "no_videos": "没有找到视频文件。请先上传或放入视频。",
        "running": "正在运行...",
        "success": "运行成功。",
        "failed": "运行失败。",
        "report_success": "报告生成成功。",
        "batch_created": "已创建批次文件夹：",
        "view_log": "查看日志",
        "completed": "已完成",
        "upload_title": "上传媒体文件",
        "upload_desc": "上传图片或视频到本地 input_media 文件夹。",
        "choose_files": "选择文件",
        "save_uploaded": "保存到 input_media",
        "saved_files": "已保存文件。",
        "input_files": "输入媒体文件",
        "no_files": "没有找到文件。",
        "keywords": "关键词",
        "summary": "摘要",
        "key_points": "重点信息",
        "archive_suggestion": "归档建议",
        "action_suggestion": "行动建议",
        "no_summary": "还没有总结结果。请先运行流程。",
        "preview_frames": "预览帧",
        "no_video_info": "还没有视频信息。请先运行视频基础信息提取。",
        "latest_reports": "主报告文件",
        "batch_reports": "批次报告文件夹",
        "download_reports": "下载报告",
        "no_reports": "还没有生成报告。",
        "next_modules": "后续模块",
        "openai_summary": "OpenAI / ChatGPT 增强总结",
        "exe_packaging": "Windows EXE 打包",
        "theme_blue": "海洋蓝",
        "theme_purple": "紫雾",
        "theme_coral": "珊瑚橙",
        "brand_badge": "Apple-style UI • Local AI Workflow",
        "quick_tip": "建议：首页先运行图片流程或视频转文字流程。",
    },
    "en": {
        "app_title": "Batch Media Insight Extractor",
        "app_subtitle": "Batch Image & Video Insight Software",
        "app_caption": "Turn batch images and videos into text, summaries, keywords, and Word/PDF reports.",
        "language": "Language",
        "theme": "Theme",
        "navigation": "Navigation",
        "dashboard": "Dashboard",
        "upload": "Upload",
        "files": "Files",
        "image_summary": "Image Summary",
        "video_info": "Video Info",
        "video_transcript": "Video Transcript",
        "reports": "Reports",
        "settings": "Settings",
        "workflow_history": "Workflow History",
        "workflow_history_title": "Workflow History and Latest Status",
        "latest_run_status": "Latest Full Workflow Status",
        "latest_log_file": "Latest Log File",
        "open_latest_log": "Open Latest Log",
        "open_latest_status": "Open Latest Status File",
        "recent_logs": "Recent Logs",
        "recent_batches": "Recent Batch Reports",
        "workflow_steps": "Workflow Step Records",
        "settings_title": "Settings and Demo Mode",
        "demo_mode_title": "Demo Mode",
        "demo_mode_desc": "Use safe demo assets to test the software, prepare showcase screenshots, and generate sample reports without exposing private files.",
        "open_demo_assets": "Open Demo Assets Folder",
        "copy_demo_to_input": "Copy Demo Assets to input_media",
        "clear_and_use_demo": "Clear input_media and Use Demo Assets",
        "confirm_clear_for_demo": "Confirm clearing input_media and switching to demo assets",
        "copied_demo": "Demo assets copied to input_media. File count: ",
        "no_demo_files": "No demo assets found. Please run VIDEO-EXTRACT-023 first.",
        "latest_batch_report": "Latest Batch Report",
        "open_latest_batch": "Open Latest Batch Report",
        "no_batch_found": "No batch report found.",
        "latest_demo_report": "Latest Demo Report",
        "open_latest_demo_report": "Open Latest Demo Report",
        "no_demo_report_found": "No demo report found.",
        "local_mode_note": "Current mode: local workflow. No OpenAI API credits are used.",
        "quality_note": "Product standard: stable, clear, safe, and long-term usable.",
        "project_folders": "Project Folders",
        "project_folder": "Project folder",
        "input_folder": "Input folder",
        "reports_folder": "Reports folder",
        "batch_folder": "Batch reports",
        "video_frames_folder": "Video frames",
        "video_transcripts_folder": "Video transcripts",
        "open_input": "Open input_media",
        "open_reports": "Open reports",
        "open_batches": "Open batches",
        "open_video_frames": "Open video_frames",
        "open_video_transcripts": "Open video_transcripts",
        "tools": "Tools",
        "confirm_clear_input": "Confirm clearing input_media",
        "confirm_clear_reports": "Confirm clearing reports",
        "clear_input": "Clear input_media",
        "clear_reports": "Clear reports",
        "clear_input_success": "input_media has been cleared.",
        "clear_reports_success": "reports has been cleared.",
        "total_files": "Total files",
        "images": "Images",
        "videos": "Videos",
        "reports_count": "Reports",
        "main_actions": "Main Actions",
        "local_full_workflow_title": "One-Click Local Full Workflow",
        "local_full_workflow_desc": "Automatically process images and videos in input_media: image OCR, video transcription, local summaries, Word/PDF reports, and batch archiving.",
        "run_local_full": "Run Local Full Workflow",
        "image_workflow_title": "Image Workflow",
        "image_workflow_desc": "Batch image OCR, text cleanup, local AI summary, and Word/PDF report generation.",
        "video_workflow_title": "Video Transcription Workflow",
        "video_workflow_desc": "Extract audio, run Whisper transcription, summarize video content, and generate Word/PDF reports.",
        "video_info_title": "Video Basic Info",
        "video_info_desc": "Extract duration, resolution, FPS, and generate video preview frames.",
        "report_center_title": "Report Center",
        "report_center_desc": "View, download, and manage generated Word/PDF reports.",
        "choose_format": "Choose image report format",
        "word_only": "Word only",
        "pdf_only": "PDF only",
        "word_pdf": "Word + PDF",
        "create_batch": "Create separate batch folder",
        "run_image": "Run Image Workflow",
        "run_video": "Run Video Transcription",
        "run_video_info": "Extract Video Info",
        "open_report_center": "Open Report Center",
        "no_images": "No image files found. Please upload or add images first.",
        "no_videos": "No video files found. Please upload or add videos first.",
        "running": "Running...",
        "success": "Run completed successfully.",
        "failed": "Run failed.",
        "report_success": "Report generated successfully.",
        "batch_created": "Batch folder created:",
        "view_log": "View log",
        "completed": "completed",
        "upload_title": "Upload Media Files",
        "upload_desc": "Upload images or videos into the local input_media folder.",
        "choose_files": "Choose files",
        "save_uploaded": "Save to input_media",
        "saved_files": "Saved file(s).",
        "input_files": "Input Media Files",
        "no_files": "No files found.",
        "keywords": "Keywords",
        "summary": "Summary",
        "key_points": "Key Points",
        "archive_suggestion": "Archive Suggestion",
        "action_suggestion": "Action Suggestion",
        "no_summary": "No summary found yet. Run the workflow first.",
        "preview_frames": "Preview Frames",
        "no_video_info": "No video information found yet. Run video info extraction first.",
        "latest_reports": "Main report files",
        "batch_reports": "Batch report folders",
        "download_reports": "Download reports",
        "no_reports": "No report files found yet.",
        "next_modules": "Next Modules",
        "openai_summary": "OpenAI / ChatGPT enhanced summary",
        "exe_packaging": "Windows EXE packaging",
        "theme_blue": "Ocean Blue",
        "theme_purple": "Lavender",
        "theme_coral": "Sunset Coral",
        "brand_badge": "Apple-style UI • Local AI Workflow",
        "quick_tip": "Tip: start from the image workflow or the video transcription workflow on the dashboard.",
    }
}


def ensure_folders():
    INPUT_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    BATCHES_DIR.mkdir(parents=True, exist_ok=True)
    VIDEO_FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    VIDEO_TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)


def open_folder(path: Path):
    path.mkdir(parents=True, exist_ok=True)
    if os.name == "nt":
        os.startfile(str(path))
    else:
        subprocess.Popen(["open", str(path)])


def clear_folder(folder: Path):
    folder.mkdir(parents=True, exist_ok=True)
    for item in folder.iterdir():
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)


def classify_file(file_path: Path):
    ext = file_path.suffix.lower()
    if ext in IMAGE_EXTENSIONS:
        return "Image"
    if ext in VIDEO_EXTENSIONS:
        return "Video"
    return "Other"


def list_media_files():
    files = []
    for file_path in INPUT_DIR.rglob("*"):
        if file_path.is_file():
            files.append({
                "file_name": file_path.name,
                "type": classify_file(file_path),
                "extension": file_path.suffix.lower(),
                "size_mb": round(file_path.stat().st_size / (1024 * 1024), 3),
                "modified_time": datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                "relative_path": str(file_path.relative_to(INPUT_DIR)),
            })
    files.sort(key=lambda x: x["modified_time"], reverse=True)
    return files


def list_report_files():
    reports = []
    if REPORTS_DIR.exists():
        for file_path in REPORTS_DIR.glob("*"):
            if file_path.is_file():
                reports.append({
                    "file_name": file_path.name,
                    "extension": file_path.suffix.lower(),
                    "size_mb": round(file_path.stat().st_size / (1024 * 1024), 3),
                    "modified_time": datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                    "full_path": str(file_path.resolve()),
                })
    reports.sort(key=lambda x: x["modified_time"], reverse=True)
    return reports


def list_batch_folders():
    batches = []
    if BATCHES_DIR.exists():
        for folder in BATCHES_DIR.iterdir():
            if folder.is_dir():
                files = list(folder.glob("*"))
                batches.append({
                    "batch_name": folder.name,
                    "file_count": len([f for f in files if f.is_file()]),
                    "modified_time": datetime.fromtimestamp(folder.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                    "full_path": str(folder.resolve()),
                })
    batches.sort(key=lambda x: x["modified_time"], reverse=True)
    return batches


def load_json_file(path):
    file_path = Path(path)
    if not file_path.exists():
        return []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_uploaded_files(uploaded_files):
    saved = []
    for uploaded_file in uploaded_files:
        target_path = INPUT_DIR / uploaded_file.name
        with open(target_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        saved.append(str(target_path))
    return saved


def run_command(command):
    process = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
    )

    output = ""

    if process.stdout:
        output += process.stdout

    if process.stderr:
        output += "\n[STDERR]\n" + process.stderr

    return process.returncode, output


def run_steps(steps, text):
    for step_name, command in steps:
        st.write(f"### {step_name}")

        code, output = run_command(command)

        with st.expander(f"{text['view_log']}: {step_name}", expanded=False):
            st.code(output or "No output")

        if code != 0:
            st.error(f"{step_name} {text['failed']}.")
            return False

        st.success(f"{step_name} {text['completed']}.")

    return True


def run_image_pipeline(report_format, text):
    steps = [
        ("Step 1 | Media inventory scan", [sys.executable, "run_step_001_inventory.py"]),
        ("Step 2 | Image information", [sys.executable, "run_step_002_image_info.py"]),
        ("Step 5 | Image OCR", [sys.executable, "run_step_005_image_ocr.py"]),
        ("Step 5D | OCR text cleanup", [sys.executable, "run_step_005d_clean_ocr_text.py"]),
        ("Step 7A | Local AI summary", [sys.executable, "run_step_007a_local_ai_summary.py"]),
        ("Step 7A Report | Generate image report", [sys.executable, "run_step_007a_generate_summary_report.py", "--format", report_format]),
    ]
    return run_steps(steps, text)


def run_video_info_pipeline(text):
    steps = [
        ("Step 9 | Video info and preview frames", [sys.executable, "run_step_009_video_info.py"]),
    ]
    return run_steps(steps, text)


def run_video_transcript_pipeline(text):
    steps = [
        ("Step 9 | Video info and preview frames", [sys.executable, "run_step_009_video_info.py"]),
        ("Step 10 | Video audio extraction", [sys.executable, "run_step_010_video_audio_extract.py"]),
        ("Step 11 | Whisper transcription", [sys.executable, "run_step_011_video_transcribe.py"]),
        ("Step 12 | Video summary report", [sys.executable, "run_step_012_video_summary_report.py"]),
    ]
    return run_steps(steps, text)


def run_local_full_workflow_pipeline(text):
    import os
    import json
    from datetime import datetime

    st.write("### Step 15 | Local full workflow runner")

    logs_dir = OUTPUT_DIR / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = logs_dir / f"web_local_full_workflow_{timestamp}.log"

    status_json = OUTPUT_DIR / "last_local_full_workflow_status.json"
    status_txt = OUTPUT_DIR / "last_local_full_workflow_status.txt"

    command = [
        sys.executable,
        "-u",
        "run_step_015_local_full_workflow.py",
        "--format",
        "both"
    ]

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    st.info(f"Running local full workflow. Log file: {log_path}")

    with open(log_path, "w", encoding="utf-8", errors="ignore") as log_file:
        process = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="ignore",
            env=env
        )

    log_text = ""
    if log_path.exists():
        try:
            log_text = log_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            log_text = ""

    with st.expander(f"{text['view_log']}: Step 15 | Local full workflow runner", expanded=True):
        if log_text:
            st.code(log_text[-8000:])
        else:
            st.code("No log text found.")

    status_data = {}

    if status_json.exists():
        try:
            status_data = json.loads(status_json.read_text(encoding="utf-8"))
        except Exception as e:
            st.warning(f"Could not read status JSON: {e}")

    if status_txt.exists():
        try:
            status_text = status_txt.read_text(encoding="utf-8", errors="ignore")
            with st.expander("Last local full workflow status", expanded=True):
                st.code(status_text)
        except Exception:
            pass

    status_success = bool(status_data.get("overall_success"))

    if process.returncode == 0 and status_success:
        st.success("Step 15 completed successfully.")
        return True

    st.error("Step 15 failed or status file did not confirm success.")
    st.write(f"Return code: {process.returncode}")
    st.write(f"Status overall_success: {status_data.get('overall_success', 'missing')}")
    st.write(f"Log file: {log_path}")
    return False


def create_batch_report_archive(report_names):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    batch_dir = BATCHES_DIR / timestamp
    batch_dir.mkdir(parents=True, exist_ok=True)

    copied = []
    for name in report_names:
        source = REPORTS_DIR / name
        if source.exists():
            target = batch_dir / f"{timestamp}_{source.name}"
            shutil.copy2(source, target)
            copied.append(str(target))

    return batch_dir, copied


def download_file_button(file_path: str):
    path = Path(file_path)
    if not path.exists():
        return

    with open(path, "rb") as f:
        data = f.read()

    st.download_button(
        label=f"Download {path.name}",
        data=data,
        file_name=path.name,
        mime="application/octet-stream",
        key=f"download_{path.name}_{path.stat().st_mtime}"
    )


def apply_apple_style(theme):
    st.markdown(
        f"""
        <style>
        :root {{
            --accent: {theme['accent']};
            --accent-soft: {theme['accent_soft']};
            --accent-2: {theme['accent_2']};
            --glow: {theme['glow']};
            --hero-grad-1: {theme['hero_grad_1']};
            --hero-grad-2: {theme['hero_grad_2']};
            --badge-bg: {theme['badge_bg']};
            --badge-text: {theme['badge_text']};
            --button-text: {theme['button_text']};
        }}

        .stApp {{
            background:
                radial-gradient(circle at top left, var(--glow), transparent 28%),
                radial-gradient(circle at 90% 10%, rgba(255,255,255,0.65), transparent 25%),
                linear-gradient(180deg, #f7f8fb 0%, #ffffff 50%, #f5f5f7 100%);
            color: #1d1d1f;
        }}

        section[data-testid="stSidebar"] {{
            background: rgba(246, 247, 249, 0.94);
            border-right: 1px solid rgba(0, 0, 0, 0.06);
        }}

        .block-container {{
            padding-top: 2.4rem;
            padding-bottom: 4rem;
            max-width: 1200px;
        }}

        h1 {{
            font-size: 3.55rem !important;
            line-height: 1.02 !important;
            letter-spacing: -0.065em;
            font-weight: 820 !important;
        }}

        h2, h3 {{
            letter-spacing: -0.035em;
        }}

        div[data-testid="stMetric"] {{
            background: rgba(255, 255, 255, 0.84);
            border: 1px solid rgba(0, 0, 0, 0.06);
            padding: 18px 20px;
            border-radius: 28px;
            box-shadow: 0 16px 34px rgba(0, 0, 0, 0.055);
            position: relative;
            overflow: hidden;
        }}

        div[data-testid="stMetric"]::before {{
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 4px;
            background: linear-gradient(90deg, var(--accent), var(--accent-2));
        }}

        .hero-card {{
            background:
                linear-gradient(135deg, var(--hero-grad-1) 0%, var(--hero-grad-2) 100%),
                rgba(255, 255, 255, 0.84);
            border: 1px solid rgba(0, 0, 0, 0.06);
            border-radius: 36px;
            padding: 40px 44px;
            box-shadow: 0 24px 60px rgba(0, 0, 0, 0.07);
            margin-bottom: 26px;
            backdrop-filter: blur(18px);
        }}

        .brand-badge {{
            display: inline-block;
            padding: 8px 14px;
            border-radius: 999px;
            background: var(--badge-bg);
            color: var(--badge-text);
            font-size: 0.85rem;
            font-weight: 600;
            margin-bottom: 12px;
        }}

        .hero-subtitle {{
            font-size: 1.18rem;
            color: #505057;
            margin-top: -4px;
            margin-bottom: 0.35rem;
            font-weight: 600;
        }}

        .hero-caption {{
            font-size: 1.02rem;
            color: #70707a;
            margin-top: 0.5rem;
            max-width: 760px;
        }}

        .tip-card {{
            background: rgba(255,255,255,0.78);
            border: 1px solid rgba(0,0,0,0.06);
            border-radius: 22px;
            padding: 14px 18px;
            margin-top: 18px;
            color: #5f6470;
            box-shadow: 0 12px 28px rgba(0,0,0,0.04);
        }}

        .action-card {{
            background: rgba(255, 255, 255, 0.84);
            border: 1px solid rgba(0, 0, 0, 0.065);
            border-radius: 30px;
            padding: 24px 24px 18px 24px;
            box-shadow: 0 18px 46px rgba(0, 0, 0, 0.06);
            min-height: 200px;
            margin-bottom: 16px;
            position: relative;
            overflow: hidden;
        }}

        .action-card::before {{
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 5px;
            background: linear-gradient(90deg, var(--accent), var(--accent-2));
        }}

        .action-icon {{
            width: 48px;
            height: 48px;
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: var(--accent-soft);
            font-size: 1.35rem;
            margin-bottom: 14px;
        }}

        .action-card h3 {{
            font-size: 1.35rem;
            margin-bottom: 0.35rem;
        }}

        .action-card p {{
            color: #6e6e73;
            font-size: 0.98rem;
            line-height: 1.58;
        }}

        .stButton > button {{
            border-radius: 999px;
            border: 1px solid rgba(0,0,0,0.08);
            box-shadow: 0 8px 20px rgba(0,0,0,0.055);
            transition: all 0.18s ease;
            padding: 0.56rem 1.10rem;
        }}

        .stButton > button[kind="primary"] {{
            background: linear-gradient(135deg, var(--accent), var(--accent-2));
            color: var(--button-text);
            border: none;
        }}

        .stButton > button:hover {{
            transform: translateY(-1px);
            box-shadow: 0 14px 30px rgba(0,0,0,0.09);
        }}

        div[data-testid="stAlert"] {{
            border-radius: 22px;
            border: 1px solid rgba(0,0,0,0.06);
        }}

        div[data-testid="stExpander"] {{
            border-radius: 22px;
            border: 1px solid rgba(0,0,0,0.06);
            background: rgba(255,255,255,0.76);
        }}

        div[data-baseweb="select"] > div,
        div[data-baseweb="base-input"] {{
            border-radius: 18px !important;
        }}

        .section-space {{
            margin-top: 10px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


def apply_layout_polish():
    st.markdown(
        """
        <style>
        .block-container {
            max-width: 1180px;
            padding-left: 3rem;
            padding-right: 3rem;
        }

        .hero-card {
            border-radius: 38px;
            padding: 44px 48px;
        }

        .hero-card h1 {
            font-size: clamp(2.6rem, 5vw, 4.2rem) !important;
            letter-spacing: -0.07em;
        }

        .settings-status-card {
            background: rgba(255,255,255,0.86);
            border: 1px solid rgba(0,0,0,0.065);
            border-radius: 28px;
            padding: 20px 22px;
            min-height: 142px;
            box-shadow: 0 18px 42px rgba(0,0,0,0.055);
            position: relative;
            overflow: hidden;
        }

        .settings-status-card::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 5px;
            background: linear-gradient(90deg, var(--accent), var(--accent-2));
        }

        .settings-status-card .status-label {
            font-size: 0.92rem;
            font-weight: 720;
            color: #1d1d1f;
            white-space: nowrap;
            margin-bottom: 16px;
        }

        .settings-status-card .status-value {
            font-size: 2.05rem;
            line-height: 1;
            font-weight: 780;
            letter-spacing: -0.04em;
            color: #1d1d1f;
            margin-bottom: 12px;
        }

        .settings-status-card .status-caption {
            font-size: 0.88rem;
            color: #6e6e73;
            line-height: 1.35;
        }

        section[data-testid="stSidebar"] code {
            font-size: 0.76rem !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            display: block;
            max-width: 100%;
        }

        div[data-testid="stHorizontalBlock"] {
            gap: 1.1rem;
        }

        .stButton > button {
            min-height: 44px;
            font-weight: 650;
        }

        div[data-testid="stMetric"] {
            min-height: 118px;
        }

        div[data-testid="stMetricLabel"] {
            white-space: nowrap;
        }

        @media (max-width: 900px) {
            .block-container {
                padding-left: 1.25rem;
                padding-right: 1.25rem;
            }
            .hero-card {
                padding: 32px 30px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def render_action_card(icon, title, desc):
    st.markdown(
        f"""
        <div class="action-card">
            <div class="action-icon">{icon}</div>
            <h3>{title}</h3>
            <p>{desc}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_hero(text, media_files, reports):
    image_count = sum(1 for item in media_files if item["type"] == "Image")
    video_count = sum(1 for item in media_files if item["type"] == "Video")

    st.markdown(
        f"""
        <div class="hero-card">
            <div class="brand-badge">{text['brand_badge']}</div>
            <h1>{text['app_title']}</h1>
            <p class="hero-subtitle">{text['app_subtitle']}</p>
            <p class="hero-caption">{text['app_caption']}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(text["total_files"], len(media_files))
    col2.metric(text["images"], image_count)
    col3.metric(text["videos"], video_count)
    col4.metric(text["reports_count"], len(reports))

    st.markdown(f'<div class="tip-card">💡 {text["quick_tip"]}</div>', unsafe_allow_html=True)

    return image_count, video_count


def run_image_from_dashboard(image_count, text):
    report_format_label = st.selectbox(
        text["choose_format"],
        [text["word_only"], text["pdf_only"], text["word_pdf"]],
        index=0,
        key="dashboard_image_format"
    )

    format_map = {
        text["word_only"]: "word",
        text["pdf_only"]: "pdf",
        text["word_pdf"]: "both",
    }

    report_format = format_map[report_format_label]
    create_batch = st.checkbox(text["create_batch"], value=True, key="dashboard_image_batch")

    if st.button(text["run_image"], type="primary", key="dashboard_run_image"):
        if image_count == 0:
            st.error(text["no_images"])
        else:
            with st.status(text["running"], expanded=True) as status:
                success = run_image_pipeline(report_format, text)

                if success:
                    if create_batch:
                        names = []
                        if report_format in ["word", "both"]:
                            names.append("image_ai_summary_local_report.docx")
                        if report_format in ["pdf", "both"]:
                            names.append("image_ai_summary_local_report.pdf")
                        batch_dir, _ = create_batch_report_archive(names)
                        st.success(f"{text['batch_created']} {batch_dir}")
                    status.update(label=text["success"], state="complete")
                    st.success(text["report_success"])
                    st.balloons()
                else:
                    status.update(label=text["failed"], state="error")


def run_video_from_dashboard(video_count, text):
    create_batch = st.checkbox(text["create_batch"], value=True, key="dashboard_video_batch")

    if st.button(text["run_video"], type="primary", key="dashboard_run_video"):
        if video_count == 0:
            st.error(text["no_videos"])
        else:
            with st.status(text["running"], expanded=True) as status:
                success = run_video_transcript_pipeline(text)

                if success:
                    if create_batch:
                        batch_dir, _ = create_batch_report_archive([
                            "video_summary_local_report.docx",
                            "video_summary_local_report.pdf",
                        ])
                        st.success(f"{text['batch_created']} {batch_dir}")
                    status.update(label=text["success"], state="complete")
                    st.success(text["report_success"])
                    st.balloons()
                else:
                    status.update(label=text["failed"], state="error")


def render_dashboard(text, image_count, video_count):
    st.markdown(f"## {text['main_actions']}")

    render_action_card("🚀", text["local_full_workflow_title"], text["local_full_workflow_desc"])

    if st.button(text["run_local_full"], type="primary", key="dashboard_run_local_full"):
        with st.status(text["running"], expanded=True) as status:
            success = run_local_full_workflow_pipeline(text)

            if success:
                status.update(label=text["success"], state="complete")
                st.success(text["report_success"])
                st.balloons()
            else:
                status.update(label=text["failed"], state="error")

    st.divider()
    row1_col1, row1_col2 = st.columns(2)

    with row1_col1:
        render_action_card("🖼️", text["image_workflow_title"], text["image_workflow_desc"])
        run_image_from_dashboard(image_count, text)

    with row1_col2:
        render_action_card("🎬", text["video_workflow_title"], text["video_workflow_desc"])
        run_video_from_dashboard(video_count, text)

    row2_col1, row2_col2 = st.columns(2)

    with row2_col1:
        render_action_card("📹", text["video_info_title"], text["video_info_desc"])
        if st.button(text["run_video_info"], type="primary", key="dashboard_video_info"):
            if video_count == 0:
                st.error(text["no_videos"])
            else:
                with st.status(text["running"], expanded=True) as status:
                    success = run_video_info_pipeline(text)
                    if success:
                        status.update(label=text["success"], state="complete")
                        st.success(text["success"])
                    else:
                        status.update(label=text["failed"], state="error")

    with row2_col2:
        render_action_card("📄", text["report_center_title"], text["report_center_desc"])
        if st.button(text["open_report_center"], key="dashboard_reports"):
            open_folder(REPORTS_DIR)


def render_upload_page(text):
    st.header(text["upload_title"])
    st.write(text["upload_desc"])

    uploaded_files = st.file_uploader(
        text["choose_files"],
        type=[
            "jpg", "jpeg", "png", "webp", "bmp", "gif", "tiff", "tif", "heic", "heif", "avif",
            "mp4", "mov", "avi", "mkv", "webm", "flv", "wmv", "m4v", "mpeg", "mpg", "3gp", "ts"
        ],
        accept_multiple_files=True
    )

    if uploaded_files:
        if st.button(text["save_uploaded"], type="primary"):
            saved = save_uploaded_files(uploaded_files)
            st.success(f"{len(saved)} {text['saved_files']}")
            for path in saved:
                st.code(path)


def render_files_page(text, media_files):
    st.header(text["input_files"])
    if media_files:
        st.dataframe(pd.DataFrame(media_files), width="stretch")
    else:
        st.warning(text["no_files"])


def render_image_summary_page(text):
    st.header(text["image_summary"])
    items = load_json_file(OUTPUT_DIR / "image_ai_summary_local.json")

    if not items:
        st.caption(text["no_summary"])
        return

    for item in items:
        with st.expander(f"{item.get('file_name', '')} | {item.get('content_type', '')}", expanded=False):
            st.write(f"**{text['keywords']}**")
            st.write("、".join(item.get("keywords", [])))
            st.write(f"**{text['summary']}**")
            st.write(item.get("summary", ""))
            st.write(f"**{text['key_points']}**")
            for index, point in enumerate(item.get("key_points", []), start=1):
                st.write(f"{index}. {point}")
            st.write(f"**{text['archive_suggestion']}**")
            st.write(item.get("archive_suggestion", ""))


def render_video_info_page(text):
    st.header(text["video_info"])

    if st.button(text["run_video_info"], type="primary", key="video_info_page_button"):
        with st.status(text["running"], expanded=True) as status:
            success = run_video_info_pipeline(text)
            if success:
                status.update(label=text["success"], state="complete")
            else:
                status.update(label=text["failed"], state="error")

    items = load_json_file(OUTPUT_DIR / "video_basic_info.json")

    if not items:
        st.warning(text["no_video_info"])
        return

    rows = []
    for item in items:
        rows.append({
            "file_name": item.get("file_name", ""),
            "dimension": f"{item.get('width', '')}x{item.get('height', '')}",
            "duration": item.get("duration_hms", ""),
            "fps": item.get("fps", ""),
            "size_mb": item.get("size_mb", ""),
            "preview_frames": item.get("preview_frame_count", 0),
        })

    st.dataframe(pd.DataFrame(rows), width="stretch")

    for item in items:
        with st.expander(f"{item.get('file_name', '')} | {item.get('duration_hms', '')}", expanded=False):
            frames = item.get("preview_frames", [])
            if frames:
                st.write(f"**{text['preview_frames']}**")
                cols = st.columns(min(3, len(frames)))
                for i, frame_path in enumerate(frames):
                    path = Path(frame_path)
                    if path.exists():
                        with cols[i % len(cols)]:
                            st.image(str(path), caption=path.name, width="stretch")


def render_video_transcript_page(text, video_count):
    st.header(text["video_transcript"])

    if st.button(text["run_video"], type="primary", key="video_transcript_page_button"):
        if video_count == 0:
            st.error(text["no_videos"])
        else:
            with st.status(text["running"], expanded=True) as status:
                success = run_video_transcript_pipeline(text)
                if success:
                    status.update(label=text["success"], state="complete")
                    st.success(text["report_success"])
                else:
                    status.update(label=text["failed"], state="error")

    items = load_json_file(OUTPUT_DIR / "video_summary_local.json")

    if not items:
        st.caption(text["no_summary"])
        return

    for item in items:
        with st.expander(f"{item.get('file_name', '')} | {item.get('content_type', '')}", expanded=False):
            st.write(f"**{text['keywords']}**")
            st.write("、".join(item.get("keywords", [])))
            st.write(f"**{text['summary']}**")
            st.write(item.get("summary", ""))
            st.write(f"**{text['key_points']}**")
            for index, point in enumerate(item.get("key_points", []), start=1):
                st.write(f"{index}. {point}")
            st.write(f"**{text['action_suggestion']}**")
            st.write(item.get("action_suggestion", ""))
            with st.expander("Transcript / 转写全文", expanded=False):
                st.write(item.get("cleaned_text", ""))


def render_reports_page(text):
    st.header(text["reports"])

    reports = list_report_files()
    batches = list_batch_folders()

    st.subheader(text["latest_reports"])
    if reports:
        st.dataframe(pd.DataFrame(reports), width="stretch")
        st.write(text["download_reports"])
        for item in reports:
            download_file_button(item["full_path"])
    else:
        st.caption(text["no_reports"])

    st.subheader(text["batch_reports"])
    if batches:
        st.dataframe(pd.DataFrame(batches), width="stretch")
    else:
        st.caption(text["no_reports"])



def get_latest_folder(folder, prefix=None):
    folder = Path(folder)
    if not folder.exists():
        return None
    items = []
    for item in folder.iterdir():
        if item.is_dir():
            if prefix is None or item.name.startswith(prefix):
                items.append(item)
    if not items:
        return None
    items.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return items[0]


def count_folder_files(folder, recursive=False):
    folder = Path(folder)
    if not folder.exists():
        return 0
    if recursive:
        return len([p for p in folder.rglob("*") if p.is_file()])
    return len([p for p in folder.iterdir() if p.is_file()])


def folder_display_info(folder):
    folder = Path(folder)
    if not folder.exists():
        return "Not found"
    modified = datetime.fromtimestamp(folder.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
    file_count = count_folder_files(folder, recursive=True)
    return f"{folder.name} | {modified} | {file_count} files"


def copy_demo_assets_to_input(clear_existing=False):
    demo_input = PROJECT_ROOT / "demo_assets" / "input_media_demo"
    if not demo_input.exists():
        return 0
    supported = IMAGE_EXTENSIONS.union(VIDEO_EXTENSIONS)
    demo_files = []
    for item in demo_input.iterdir():
        if item.is_file() and item.suffix.lower() in supported:
            demo_files.append(item)
    if not demo_files:
        return 0
    if clear_existing:
        clear_folder(INPUT_DIR)
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    count = 0
    for item in demo_files:
        shutil.copy2(item, INPUT_DIR / item.name)
        count += 1
    return count


def render_small_status_card(title, value, caption):
    html = (
        "<div class=\"settings-status-card\">"
        f"<div class=\"status-label\">{title}</div>"
        f"<div class=\"status-value\">{value}</div>"
        f"<div class=\"status-caption\">{caption}</div>"
        "</div>"
    )
    st.markdown(html, unsafe_allow_html=True)

def render_settings_page(text):
    st.header(text.get("settings_title", "Settings and Demo Mode"))
    st.info(text.get("local_mode_note", "Current mode: local workflow. No OpenAI API credits are used."))
    st.write(text.get("quality_note", "Product standard: stable, clear, safe, and long-term usable."))

    demo_input = PROJECT_ROOT / "demo_assets" / "input_media_demo"
    sample_reports = PROJECT_ROOT / "demo_assets" / "sample_reports"
    latest_batch = get_latest_folder(BATCHES_DIR)
    latest_demo = get_latest_folder(sample_reports, prefix="demo_run_")

    input_count = count_folder_files(INPUT_DIR, recursive=True)
    demo_count = count_folder_files(demo_input, recursive=False)
    report_count = count_folder_files(REPORTS_DIR, recursive=False)
    log_count = count_folder_files(OUTPUT_DIR / "logs", recursive=False)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_small_status_card("Input Files", input_count, "input_media")
    with col2:
        render_small_status_card("Demo Files", demo_count, "Safe demo assets")
    with col3:
        render_small_status_card("Reports", report_count, "Main reports")
    with col4:
        render_small_status_card("Logs", log_count, "Workflow logs")

    st.divider()
    st.subheader(text.get("demo_mode_title", "Demo Mode"))
    st.write(text.get("demo_mode_desc", "Use safe demo assets to test the software and prepare public showcase materials."))

    quick1, quick2, quick3 = st.columns(3)
    with quick1:
        if st.button("打开 input_media / Open input_media", key="settings_open_input_media"):
            open_folder(INPUT_DIR)
    with quick2:
        if st.button("打开 reports / Open reports", key="settings_open_reports"):
            open_folder(REPORTS_DIR)
    with quick3:
        if st.button("打开 logs / Open logs", key="settings_open_logs"):
            open_folder(OUTPUT_DIR / "logs")

    st.markdown("### Demo Controls")
    c1, c2 = st.columns(2)
    with c1:
        if st.button(text.get("open_demo_assets", "Open Demo Assets Folder"), key="settings_open_demo_assets"):
            open_folder(demo_input)
    with c2:
        if st.button(text.get("copy_demo_to_input", "Copy Demo Assets to input_media"), type="primary", key="settings_copy_demo"):
            count = copy_demo_assets_to_input(clear_existing=False)
            if count > 0:
                st.success(text.get("copied_demo", "Demo assets copied to input_media. File count: ") + str(count))
            else:
                st.error(text.get("no_demo_files", "No demo assets found."))

    st.warning("危险操作：下面的按钮会先清空 input_media，再复制 Demo 素材。请确认当前 input_media 里的私人文件已经备份。")
    confirm_demo_clear = st.checkbox(text.get("confirm_clear_for_demo", "Confirm clearing input_media and switching to demo assets"), key="settings_confirm_demo_clear")
    if st.button(text.get("clear_and_use_demo", "Clear input_media and Use Demo Assets"), disabled=not confirm_demo_clear, key="settings_clear_and_demo"):
        count = copy_demo_assets_to_input(clear_existing=True)
        if count > 0:
            st.success(text.get("copied_demo", "Demo assets copied to input_media. File count: ") + str(count))
        else:
            st.error(text.get("no_demo_files", "No demo assets found."))

    st.divider()
    left, right = st.columns(2)
    with left:
        st.subheader(text.get("latest_batch_report", "Latest Batch Report"))
        if latest_batch:
            st.caption(folder_display_info(latest_batch))
            st.code(str(latest_batch))
            if st.button(text.get("open_latest_batch", "Open Latest Batch Report"), key="settings_open_latest_batch"):
                open_folder(latest_batch)
        else:
            st.warning(text.get("no_batch_found", "No batch report found."))
    with right:
        st.subheader(text.get("latest_demo_report", "Latest Demo Report"))
        if latest_demo:
            st.caption(folder_display_info(latest_demo))
            st.code(str(latest_demo))
            if st.button(text.get("open_latest_demo_report", "Open Latest Demo Report"), key="settings_open_latest_demo"):
                open_folder(latest_demo)
        else:
            st.warning(text.get("no_demo_report_found", "No demo report found."))

    st.divider()
    with st.expander("Settings Quality Checklist / 设置页质量检查", expanded=False):
        st.write("- Demo 操作必须安全可控")
        st.write("- 清空 input_media 必须二次确认")
        st.write("- 报告文件夹必须能快速打开")
        st.write("- 本地模式必须不消耗 API credits")
        st.write("- 后续可以继续加入更多设置项")


def load_json_safely(path):
    path = Path(path)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def get_latest_file(folder, pattern="*"):
    folder = Path(folder)
    if not folder.exists():
        return None
    files = [p for p in folder.glob(pattern) if p.is_file()]
    if not files:
        return None
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0]


def get_recent_files(folder, pattern="*", limit=10):
    folder = Path(folder)
    if not folder.exists():
        return []
    files = [p for p in folder.glob(pattern) if p.is_file()]
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files[:limit]


def get_recent_folders(folder, prefix=None, limit=10):
    folder = Path(folder)
    if not folder.exists():
        return []
    folders = []
    for item in folder.iterdir():
        if item.is_dir():
            if prefix is None or item.name.startswith(prefix):
                folders.append(item)
    folders.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return folders[:limit]


def open_path(path):
    path = Path(path)
    if not path.exists():
        return
    if os.name == "nt":
        os.startfile(str(path))
    else:
        subprocess.Popen(["open", str(path)])


def path_row(path):
    path = Path(path)
    modified = datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
    size_kb = round(path.stat().st_size / 1024, 2) if path.is_file() else ""
    return {"name": path.name, "modified_time": modified, "size_kb": size_kb, "path": str(path)}


def render_workflow_history_page(text):
    st.header(text.get("workflow_history_title", "Workflow History and Latest Status"))
    st.info(text.get("local_mode_note", "Current mode: local workflow. No OpenAI API credits are used."))

    status_json = OUTPUT_DIR / "last_local_full_workflow_status.json"
    status_txt = OUTPUT_DIR / "last_local_full_workflow_status.txt"
    logs_dir = OUTPUT_DIR / "logs"
    latest_log = get_latest_file(logs_dir, "*.log")
    latest_batch = get_latest_folder(BATCHES_DIR) if "get_latest_folder" in globals() else None
    latest_demo_result = get_latest_file(PROJECT_ROOT / "public_showcase_notes", "step_024_demo_workflow_result.json")
    status = load_json_safely(status_json)

    st.subheader(text.get("latest_run_status", "Latest Full Workflow Status"))
    success_value = "True" if status.get("overall_success") else "False"
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Success", success_value)
    c2.metric("Images", status.get("images_found", 0))
    c3.metric("Videos", status.get("videos_found", 0))
    c4.metric("Other", status.get("other_found", 0))

    if status:
        st.caption("Last generated time: " + str(status.get("generated_time", "")))
        if status.get("batch_folder") is not None:
            st.code(str(status.get("batch_folder", "")))
    else:
        st.warning("No local full workflow status found yet.")

    action_col1, action_col2, action_col3 = st.columns(3)
    with action_col1:
        if latest_log and st.button(text.get("open_latest_log", "Open Latest Log"), key="history_open_latest_log"):
            open_path(latest_log)
    with action_col2:
        if status_txt.exists() and st.button(text.get("open_latest_status", "Open Latest Status File"), key="history_open_status_txt"):
            open_path(status_txt)
    with action_col3:
        if latest_batch and st.button(text.get("open_latest_batch", "Open Latest Batch Report"), key="history_open_latest_batch"):
            open_folder(latest_batch)

    st.divider()
    st.subheader(text.get("workflow_steps", "Workflow Step Records"))
    steps = status.get("steps", []) if isinstance(status, dict) else []
    if steps:
        rows = []
        for item in steps:
            rows.append({"step_name": item.get("step_name", ""), "success": item.get("success", ""), "return_code": item.get("return_code", "")})
        st.dataframe(pd.DataFrame(rows), width="stretch")
    else:
        st.caption("No workflow step records found.")

    st.divider()
    left, right = st.columns(2)
    with left:
        st.subheader(text.get("recent_logs", "Recent Logs"))
        recent_logs = get_recent_files(logs_dir, "*.log", limit=10)
        if recent_logs:
            st.dataframe(pd.DataFrame([path_row(p) for p in recent_logs]), width="stretch")
        else:
            st.caption("No log files found.")
    with right:
        st.subheader(text.get("recent_batches", "Recent Batch Reports"))
        recent_batches = get_recent_folders(BATCHES_DIR, limit=10)
        if recent_batches:
            batch_rows = []
            for folder in recent_batches:
                modified = datetime.fromtimestamp(folder.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                file_count = len([p for p in folder.rglob("*") if p.is_file()])
                batch_rows.append({"batch_name": folder.name, "modified_time": modified, "file_count": file_count, "path": str(folder)})
            st.dataframe(pd.DataFrame(batch_rows), width="stretch")
        else:
            st.caption("No batch report folders found.")

    st.divider()
    with st.expander("Raw latest status JSON", expanded=False):
        st.json(status if status else {})
    if latest_log:
        with st.expander(text.get("latest_log_file", "Latest Log File"), expanded=False):
            try:
                log_text = latest_log.read_text(encoding="utf-8", errors="ignore")
                st.code(log_text[-8000:])
            except Exception as e:
                st.write(str(e))



def render_sidebar(text):
    with st.sidebar:
        st.header(text["project_folders"])

        st.write(text["project_folder"])
        st.code(str(PROJECT_ROOT))

        st.write(text["input_folder"])
        st.code(str(INPUT_DIR))

        st.write(text["reports_folder"])
        st.code(str(REPORTS_DIR))

        st.write(text["batch_folder"])
        st.code(str(BATCHES_DIR))

        st.write(text["video_frames_folder"])
        st.code(str(VIDEO_FRAMES_DIR))

        st.write(text["video_transcripts_folder"])
        st.code(str(VIDEO_TRANSCRIPTS_DIR))

        if st.button(text["open_input"]):
            open_folder(INPUT_DIR)
        if st.button(text["open_reports"]):
            open_folder(REPORTS_DIR)
        if st.button(text["open_batches"]):
            open_folder(BATCHES_DIR)
        if st.button(text["open_video_frames"]):
            open_folder(VIDEO_FRAMES_DIR)
        if st.button(text["open_video_transcripts"]):
            open_folder(VIDEO_TRANSCRIPTS_DIR)

        st.divider()
        st.header(text["tools"])

        confirm_input = st.checkbox(text["confirm_clear_input"])
        if st.button(text["clear_input"], disabled=not confirm_input):
            clear_folder(INPUT_DIR)
            st.success(text["clear_input_success"])

        confirm_reports = st.checkbox(text["confirm_clear_reports"])
        if st.button(text["clear_reports"], disabled=not confirm_reports):
            clear_folder(REPORTS_DIR)
            BATCHES_DIR.mkdir(parents=True, exist_ok=True)
            st.success(text["clear_reports_success"])

        st.divider()
        st.header(text["next_modules"])
        st.caption(text["openai_summary"])
        st.caption(text["exe_packaging"])


def main():
    ensure_folders()

    st.set_page_config(
        page_title="Batch Media Insight Extractor",
        page_icon="📷",
        layout="wide",
    )

    with st.sidebar:
        language_label = st.radio("Language / 语言", ["中文", "English"], index=0, horizontal=True)

    lang = "zh" if language_label == "中文" else "en"
    text = TEXT[lang]

    theme_options = {
        text["theme_blue"]: "Ocean Blue",
        text["theme_purple"]: "Lavender",
        text["theme_coral"]: "Sunset Coral",
    }

    with st.sidebar:
        theme_label = st.selectbox(text["theme"], list(theme_options.keys()), index=0)

    theme_key = theme_options[theme_label]
    theme = THEMES[theme_key]

    apply_apple_style(theme)
    apply_layout_polish()

    with st.sidebar:
        page = st.radio(
            text["navigation"],
            [
                text["dashboard"],
                text["upload"],
                text["files"],
                text["image_summary"],
                text["video_info"],
                text["video_transcript"],
                text["reports"],
                text["settings"],
                text["workflow_history"],
            ],
            index=0
        )

    render_sidebar(text)

    media_files = list_media_files()
    reports = list_report_files()
    image_count, video_count = render_hero(text, media_files, reports)

    st.divider()

    if page == text["dashboard"]:
        render_dashboard(text, image_count, video_count)
    elif page == text["upload"]:
        render_upload_page(text)
    elif page == text["files"]:
        render_files_page(text, media_files)
    elif page == text["image_summary"]:
        render_image_summary_page(text)
    elif page == text["video_info"]:
        render_video_info_page(text)
    elif page == text["video_transcript"]:
        render_video_transcript_page(text, video_count)
    elif page == text["reports"]:
        render_reports_page(text)
    elif page == text["settings"]:
        render_settings_page(text)
    elif page == text["workflow_history"]:
        render_workflow_history_page(text)


if __name__ == "__main__":
    main()
