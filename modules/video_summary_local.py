from pathlib import Path
import json
import csv
import re
from collections import Counter


STOPWORDS = {
    "的", "了", "和", "是", "在", "与", "及", "或", "为", "以", "将", "把", "对", "中", "上", "下",
    "你", "我", "他", "她", "它", "们", "这个", "那个", "就是", "然后", "因为", "所以", "如果",
    "the", "and", "or", "to", "of", "in", "for", "with", "a", "an", "is", "are", "be", "as", "on"
}


CONTENT_TYPE_RULES = [
    ("销售/营销/客户沟通视频", ["销售", "客户", "成交", "转化", "沟通", "产品", "卖点", "朋友圈", "对话", "市场", "营销"]),
    ("AI/提示词/内容创作视频", ["AI", "提示词", "生成", "图片", "视频", "内容", "脚本", "账号", "爆款", "流量"]),
    ("课程/学习/培训视频", ["课程", "学习", "培训", "考试", "作业", "知识点", "老师", "课堂", "讲解"]),
    ("商业分析/策略视频", ["商业", "策略", "市场", "品牌", "用户", "增长", "定位", "竞争", "需求"]),
    ("技术/软件/代码视频", ["代码", "Python", "软件", "项目", "运行", "报错", "模块", "系统", "接口"]),
]


def clean_transcript_text(text):
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Whisper 经常没有标点，这里做温和清理，不强行乱加标点
    text = text.strip()
    return text


def split_sentences(text):
    parts = re.split(r"[。！？!?；;\n]+", text)
    sentences = [p.strip() for p in parts if p.strip()]
    return sentences


def tokenize_keywords(text):
    chinese_terms = re.findall(r"[\u4e00-\u9fff]{2,8}", text)
    english_terms = re.findall(r"[A-Za-z][A-Za-z0-9_\-]{2,}", text)

    terms = []

    for term in chinese_terms + english_terms:
        lower = term.lower()
        if term not in STOPWORDS and lower not in STOPWORDS:
            terms.append(term)

    counter = Counter(terms)
    return [word for word, count in counter.most_common(15)]


def generate_summary(text, max_sentences=4):
    sentences = split_sentences(text)

    if not sentences:
        return ""

    selected = []

    # 优先选前面几句，因为短视频/口播通常开头给主题
    for sentence in sentences:
        if len(sentence) >= 8:
            selected.append(sentence)

        if len(selected) >= max_sentences:
            break

    summary = "。".join(selected).strip()

    if summary and not summary.endswith(("。", ".", "！", "？")):
        summary += "。"

    return summary


def score_sentence(sentence, keywords):
    score = 0

    for keyword in keywords:
        if keyword in sentence:
            score += 2

    markers = [
        "方法", "问题", "原因", "提高", "效率", "客户", "产品", "卖点", "成交", "总结",
        "重点", "建议", "步骤", "核心", "关键", "不要", "一定", "必须", "为什么"
    ]

    for marker in markers:
        if marker in sentence:
            score += 3

    if 15 <= len(sentence) <= 160:
        score += 2

    return score


def extract_key_points(text, keywords, max_points=6):
    sentences = split_sentences(text)

    scored = []

    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) < 8:
            continue

        scored.append((score_sentence(sentence, keywords), sentence))

    scored.sort(reverse=True, key=lambda x: x[0])

    points = []
    seen = set()

    for score, sentence in scored:
        if sentence in seen:
            continue

        points.append(sentence)
        seen.add(sentence)

        if len(points) >= max_points:
            break

    return points


def detect_content_type(text):
    best_type = "未知视频内容 / General Video"
    best_score = 0

    for content_type, keywords in CONTENT_TYPE_RULES:
        score = 0

        for keyword in keywords:
            if keyword.lower() in text.lower():
                score += 1

        if score > best_score:
            best_score = score
            best_type = content_type

    return best_type, best_score


def make_action_suggestion(content_type, keywords):
    keyword_text = "、".join(keywords[:6]) if keywords else "未提取关键词"

    if "销售" in content_type or "营销" in content_type:
        return f"建议归档到 销售话术/客户沟通/营销内容 文件夹；可进一步整理成话术模板、成交流程或短视频脚本。关键词：{keyword_text}。"

    if "AI" in content_type or "提示词" in content_type:
        return f"建议归档到 AI内容创作/提示词/短视频素材 文件夹；可进一步拆解为可复用提示词和内容模板。关键词：{keyword_text}。"

    if "课程" in content_type or "学习" in content_type:
        return f"建议归档到 学习资料/课程转写 文件夹；可进一步整理成笔记、复习提纲和重点清单。关键词：{keyword_text}。"

    if "商业" in content_type:
        return f"建议归档到 商业分析/策略洞察 文件夹；可进一步提炼成项目灵感、案例分析或选题方向。关键词：{keyword_text}。"

    if "技术" in content_type:
        return f"建议归档到 技术教程/项目开发记录 文件夹；可进一步提取操作步骤、命令和错误解决方案。关键词：{keyword_text}。"

    return f"建议先归档到 未分类视频转写 文件夹，后续人工确认分类。初步关键词：{keyword_text}。"


def analyze_transcription_item(item):
    raw_text = item.get("transcript_text", "")
    cleaned_text = clean_transcript_text(raw_text)

    keywords = tokenize_keywords(cleaned_text)
    summary = generate_summary(cleaned_text)
    key_points = extract_key_points(cleaned_text, keywords)
    content_type, content_type_score = detect_content_type(cleaned_text)
    action_suggestion = make_action_suggestion(content_type, keywords)

    return {
        "file_name": item.get("file_name", ""),
        "transcription_success": item.get("transcription_success", False),
        "detected_language": item.get("detected_language", ""),
        "language_probability": item.get("language_probability", ""),
        "raw_text_length": item.get("text_length", 0),
        "cleaned_text_length": len(cleaned_text),
        "content_type": content_type,
        "content_type_score": content_type_score,
        "summary": summary,
        "keywords": keywords,
        "key_points": key_points,
        "action_suggestion": action_suggestion,
        "cleaned_text": cleaned_text,
        "source_transcript": raw_text,
        "txt_output": item.get("txt_output", ""),
        "json_output": item.get("json_output", ""),
        "error_message": item.get("error_message", "")
    }


def run_video_summary(
    input_json="output/video_transcription_results.json",
    output_folder="output"
):
    input_path = Path(input_json)
    output_dir = Path(output_folder)
    output_dir.mkdir(exist_ok=True)

    if not input_path.exists():
        raise FileNotFoundError("video_transcription_results.json not found. Please run Step 11 first.")

    with open(input_path, "r", encoding="utf-8") as f:
        transcription_results = json.load(f)

    summary_results = [analyze_transcription_item(item) for item in transcription_results]

    json_path = output_dir / "video_summary_local.json"
    csv_path = output_dir / "video_summary_local.csv"
    txt_dir = output_dir / "video_summaries_local"
    txt_dir.mkdir(exist_ok=True)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary_results, f, ensure_ascii=False, indent=2)

    fieldnames = [
        "file_name",
        "transcription_success",
        "detected_language",
        "language_probability",
        "raw_text_length",
        "cleaned_text_length",
        "content_type",
        "content_type_score",
        "summary",
        "keywords",
        "key_points",
        "action_suggestion",
        "error_message"
    ]

    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for item in summary_results:
            row = dict(item)
            row["keywords"] = " | ".join(item.get("keywords", []))
            row["key_points"] = " | ".join(item.get("key_points", []))
            writer.writerow({k: row.get(k, "") for k in fieldnames})

    for item in summary_results:
        safe_name = Path(item["file_name"]).stem
        txt_path = txt_dir / f"{safe_name}_video_summary_local.txt"

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(f"File: {item['file_name']}\n")
            f.write(f"Content Type: {item['content_type']}\n")
            f.write(f"Keywords: {'、'.join(item['keywords'])}\n\n")
            f.write("Summary:\n")
            f.write(item["summary"] + "\n\n")
            f.write("Key Points:\n")
            for index, point in enumerate(item["key_points"], start=1):
                f.write(f"{index}. {point}\n")
            f.write("\nAction Suggestion:\n")
            f.write(item["action_suggestion"] + "\n\n")
            f.write("Cleaned Transcript:\n")
            f.write(item["cleaned_text"])

    return summary_results, json_path, csv_path, txt_dir
