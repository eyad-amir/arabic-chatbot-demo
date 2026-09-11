import json
import re
from pathlib import Path
from typing import Any

import streamlit as st


FALLBACK_MESSAGE = "عذراً، ليس لدي معلومات حول هذا الأمر. يرجى التواصل مع خدمة العملاء."
PROJECT_DIR = Path(__file__).resolve().parent


def load_knowledge_base() -> list[dict[str, str]] | None:
    """Load and validate FAQ entries from the local knowledge base."""
    knowledge_base_path = PROJECT_DIR / "knowledge_base.json"
    try:
        with knowledge_base_path.open("r", encoding="utf-8") as file:
            knowledge_base: Any = json.load(file)
    except FileNotFoundError:
        st.error("تعذر العثور على ملف قاعدة المعرفة knowledge_base.json.")
        return None
    except json.JSONDecodeError:
        st.error("ملف قاعدة المعرفة يحتوي على JSON غير صالح.")
        return None
    except OSError:
        st.error("تعذر قراءة ملف قاعدة المعرفة.")
        return None

    if not isinstance(knowledge_base, dict) or not knowledge_base:
        st.error("قاعدة المعرفة فارغة أو بتنسيق غير صالح.")
        return None

    entries = knowledge_base.get("knowledge_base")
    if not isinstance(entries, list) or not entries or not all(
        isinstance(entry, dict)
        and isinstance(entry.get("question"), str)
        and isinstance(entry.get("answer"), str)
        and entry["question"].strip()
        and entry["answer"].strip()
        for entry in entries
    ):
        st.error("قاعدة المعرفة لا تحتوي على معلومات صالحة.")
        return None

    return entries


def normalize_arabic(text: str) -> str:
    """Normalize Arabic text to make FAQ matching tolerant of punctuation."""
    text = text.lower()
    text = re.sub(r"[ًٌٍَُِّْـ]", "", text)
    text = re.sub(r"[إأآا]", "ا", text)
    text = re.sub(r"[ؤئ]", "ء", text)
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    return " ".join(text.split())


def answer_from_knowledge_base(
    user_input: str, entries: list[dict[str, str]]
) -> str:
    """Return an answer only when a local FAQ entry is a confident match."""
    normalized_input = normalize_arabic(user_input)
    if not normalized_input:
        return FALLBACK_MESSAGE

    input_words = set(normalized_input.split())
    best_entry: dict[str, str] | None = None
    best_score = 0.0

    for entry in entries:
        question = normalize_arabic(entry["question"])
        if normalized_input == question or normalized_input in question or question in normalized_input:
            return entry["answer"]

        question_words = set(question.split())
        score = len(input_words & question_words) / max(len(question_words), 1)
        if score > best_score:
            best_score = score
            best_entry = entry

    if best_entry is not None and best_score >= 0.5:
        return best_entry["answer"]
    return FALLBACK_MESSAGE


def display_chat_history() -> None:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def get_response_text(response: Any) -> str:
    """Return usable response text, or the required fallback message."""
    response_text = getattr(response, "text", None)
    if isinstance(response_text, str) and response_text.strip():
        return response_text.strip()
    return FALLBACK_MESSAGE


def main() -> None:
    st.title("🤖 عطور الأريج - خدمة العملاء")
    st.write("أهلاً بك! كيف يمكنني مساعدتك اليوم؟")

    entries = load_knowledge_base()
    if entries is None:
        st.stop()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    display_chat_history()

    if user_input := st.chat_input("اكتب سؤالك هنا..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            answer = answer_from_knowledge_base(user_input, entries)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.markdown(answer)


if __name__ == "__main__":
    main()