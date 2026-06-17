from pathlib import Path
import json
import csv
import re
from collections import Counter


STOPWORDS = {
    "的", "了", "和", "是", "在", "与", "及", "或", "为", "以", "将", "把", "对", "中", "上", "下",
    "the", "and", "or", "to", "of", "in", "for", "with", "a", "an", "is", "are", "be", "as", "on",
    "this", "that", "it", "you", "your", "from", "by"
}


CONTENT_TYPE_RULES = [
    ("AI Prompt / 图片生成提示词", ["生成图片", "prompt", "concept artist", "character sheet", "角色设定", "画风", "构图", "视觉规范"]),
    ("课程/学习资料", ["lecture", "assignment", "topic", "chapter", "week", "quiz", "exam", "课程", "作业", "考试", "学习", "笔记"]),
    ("商业/营销资料", ["market", "customer", "brand", "strategy", "sales", "pricing", "marketing", "客户", "品牌", "市场", "营销", "策略"]),
    ("财务/账单/报表", ["invoice", "receipt", "amount", "total", "payment", "budget", "cost", "revenue", "账单", "付款", "金额", "预算", "收入", "成本"]),
    ("聊天/社交截图", ["wechat", "message", "chat", "reply", "comment", "微信", "聊天", "评论", "回复"]),
    ("技术/代码资料", ["python", "code", "function", "error", "api", "github", "script", "代码", "函数", "报错", "接口"]),
]


def split_sentences(text: str):
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    parts = re.split(r"[。！？!?；;\n]+", text)
    sentences = [p.strip() for p in parts if p.strip()]
    return sentences


def tokenize_keywords(text: str):
    chinese_terms = re.findall(r"[\u4e00-\u9fff]{2,8}", text)
    english_terms = re.findall(r"[A-Za-z][A-Za-z0-9_\-]{2,}", text)

    terms = []
    for term in chinese_terms + english_terms:
        lower = term.lower()
        if lower not in STOPWORDS and term not in STOPWORDS:
            terms.append(term)

    counter = Counter(terms)
    return [word for word, count in counter.most_common(12)]


def score_sentence(sentence: str, keywords):
    score = 0

    for keyword in keywords:
        if keyword and keyword in sentence:
            score += 2

    important_markers = [
        "目标", "任务", "重点", "要求", "需要", "建议", "规则", "步骤", "结论",
        "goal", "task", "important", "require", "summary", "key", "must", "should"
    ]

    for marker in important_markers:
        if marker.lower() in sentence.lower():
            score += 3

    length = len(sentence)
    if 20 <= length <= 120:
        score += 2
    elif length > 160:
        score -= 1

    return score


def generate_summary(text: str, max_sentences: int = 3):
    sentences = split_sentences(text)

    if not sentences:
        return ""

    selected = sentences[:max_sentences]
    summary = "。".join(selected).strip()

    if summary and not summary.endswith(("。", ".", "！", "？")):
        summary += "。"

    return summary


def extract_key_points(text: str, keywords, max_points: int = 5):
    sentences = split_sentences(text)

    scored = []
    for sentence in sentences:
        score = score_sentence(sentence, keywords)
        scored.append((score, sentence))

    scored.sort(reverse=True, key=lambda x: x[0])

    points = []
    seen = set()

    for score, sentence in scored:
        clean = sentence.strip()
        if not clean or clean in seen:
            continue
        if len(clean) < 8:
            continue

        points.append(clean)
        seen.add(clean)

        if len(points) >= max_points:
            break

    return points


def detect_content_type(text: str):
    lower_text = text.lower()

    best_type = "未知资料 / General Document"
    best_score = 0

    for content_type, keywords in CONTENT_TYPE_RULES:
        score = 0
        for keyword in keywords:
            if keyword.lower() in lower_text:
                score += 1

        if score > best_score:
            best_score = score
            best_type = content_type

    return best_type, best_score


def make_archive_suggestion(content_type: str, keywords):
    keyword_text = "、".join(keywords[:5]) if keywords else "未提取关键词"

    if "AI Prompt" in content_type:
        return f"建议归档到 AI提示词/图片生成资料 文件夹；可按关键词：{keyword_text} 建立子分类。"

    if "课程" in content_type:
        return f"建议归档到 学习资料/OCR课堂资料 文件夹；后续可结合课程名、Week、Topic 重新命名。关键词：{keyword_text}。"

    if "商业" in content_type:
        return f"建议归档到 商业分析/市场资料 文件夹；后续可用于选题、案例分析或项目灵感。关键词：{keyword_text}。"

    if "财务" in content_type:
        return f"建议归档到 财务账单/待核对 文件夹；后续可加入金额、日期、商户识别。关键词：{keyword_text}。"

    if "聊天" in content_type:
        return f"建议归档到 聊天截图/待整理 文件夹；后续可提取对话主题、任务和跟进事项。关键词：{keyword_text}。"

    if "技术" in content_type:
        return f"建议归档到 技术资料/代码截图 文件夹；后续可提取报错、命令和解决步骤。关键词：{keyword_text}。"

    return f"建议归档到 未分类OCR资料 文件夹；后续可人工确认分类。初步关键词：{keyword_text}。"


def analyze_one_item(item):
    text = item.get("cleaned_text") or item.get("extracted_text") or ""

    keywords = tokenize_keywords(text)
    summary = generate_summary(text)
    key_points = extract_key_points(text, keywords)
    content_type, confidence_score = detect_content_type(text)
    archive_suggestion = make_archive_suggestion(content_type, keywords)

    result = {
        "file_name": item.get("file_name", ""),
        "ocr_success": item.get("ocr_success", False),
        "ocr_language": item.get("ocr_language", ""),
        "cleaned_text_length": item.get("cleaned_text_length", 0),
        "content_type": content_type,
        "content_type_score": confidence_score,
        "summary": summary,
        "keywords": keywords,
        "key_points": key_points,
        "archive_suggestion": archive_suggestion,
        "source_text": text
    }

    return result


def run_local_ai_summary(
    input_json="output/image_ocr_results_cleaned.json",
    output_folder="output"
):
    input_path = Path(input_json)
    output_dir = Path(output_folder)
    output_dir.mkdir(exist_ok=True)

    if not input_path.exists():
        raise FileNotFoundError("Cleaned OCR JSON not found. Please run Step 5D first.")

    with open(input_path, "r", encoding="utf-8") as f:
        items = json.load(f)

    results = [analyze_one_item(item) for item in items]

    json_path = output_dir / "image_ai_summary_local.json"
    csv_path = output_dir / "image_ai_summary_local.csv"
    txt_dir = output_dir / "ai_summaries_local"
    txt_dir.mkdir(exist_ok=True)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    fieldnames = [
        "file_name",
        "ocr_success",
        "ocr_language",
        "cleaned_text_length",
        "content_type",
        "content_type_score",
        "summary",
        "keywords",
        "key_points",
        "archive_suggestion"
    ]

    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for item in results:
            row = dict(item)
            row["keywords"] = " | ".join(item.get("keywords", []))
            row["key_points"] = " | ".join(item.get("key_points", []))
            row.pop("source_text", None)
            writer.writerow({k: row.get(k, "") for k in fieldnames})

    for item in results:
        safe_name = Path(item["file_name"]).stem
        txt_path = txt_dir / f"{safe_name}_ai_summary_local.txt"

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(f"File: {item['file_name']}\n")
            f.write(f"Content Type: {item['content_type']}\n")
            f.write(f"Keywords: {'、'.join(item['keywords'])}\n\n")
            f.write("Summary:\n")
            f.write(item["summary"] + "\n\n")
            f.write("Key Points:\n")
            for index, point in enumerate(item["key_points"], start=1):
                f.write(f"{index}. {point}\n")
            f.write("\nArchive Suggestion:\n")
            f.write(item["archive_suggestion"] + "\n")

    return results, json_path, csv_path, txt_dir
