"""Local FAQ engine. No external model calls."""
import json
import re
from difflib import SequenceMatcher
from pathlib import Path

FALLBACK_MESSAGE = "عذراً، ليس لدي معلومات مؤكدة حول هذا الأمر. يرجى التواصل مع خدمة العملاء."
STOP_WORDS = {"ما", "هي", "هو", "هل", "من", "في", "عن", "كم", "كيف", "اين", "يمكن", "يمكنني", "لديكم", "بكم", "الخاص", "ان", "و", "ام"}

def normalize_arabic(text: str) -> str:
    text = re.sub(r"[\u064b-\u065f\u0670ـ]", "", text.lower())
    text = re.sub("[إأآٱ]", "ا", text).replace("ى", "ي")
    return " ".join(re.sub(r"[^\w\s]", " ", text).split())

def words(text: str) -> set[str]:
    return {w[2:] if w.startswith("ال") and len(w) > 3 else w for w in normalize_arabic(text).split() if w not in STOP_WORDS}

def load_knowledge_base(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    entries = data.get("knowledge_base") if isinstance(data, dict) else None
    if not isinstance(entries, list) or not entries or not all(
        isinstance(e, dict) and all(isinstance(e.get(k), str) and e[k].strip() for k in ("question", "answer")) for e in entries
    ):
        raise ValueError("قاعدة المعرفة لا تحتوي على أسئلة وأجوبة صالحة.")
    return data

def answer_from_knowledge_base(user_input: str, entries: list[dict]) -> str:
    normalized, tokens = normalize_arabic(user_input), words(user_input)
    if not tokens:
        return FALLBACK_MESSAGE
    candidates = []
    for entry in entries:
        for alternative in entry["question"].split("/"):
            question = normalize_arabic(alternative)
            if normalized == question:
                return entry["answer"]
            expected = words(alternative)
            overlap = len(tokens & expected)
            if not overlap:
                continue
            precision, recall = overlap / len(tokens), overlap / max(len(expected), 1)
            f1 = 2 * precision * recall / (precision + recall)
            score = 0.85 * f1 + 0.15 * SequenceMatcher(None, normalized, question).ratio()
            if precision >= 0.75 and recall >= 0.5:
                candidates.append((score, entry["answer"]))
    if not candidates:
        return FALLBACK_MESSAGE
    candidates.sort(reverse=True)
    best = candidates[0]
    other = next((item for item in candidates[1:] if item[1] != best[1]), None)
    if best[0] < 0.56 or (other and best[0] - other[0] < 0.08):
        return FALLBACK_MESSAGE
    return best[1]
