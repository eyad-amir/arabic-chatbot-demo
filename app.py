"""Arabic customer-support portfolio demo with a local FAQ file."""
from pathlib import Path
import streamlit as st
from engine import load_knowledge_base, answer_from_knowledge_base

st.set_page_config(page_title="الأريج | مساعد المتجر", page_icon="✦", layout="wide")
st.markdown("""
<style>
html, body, [class*="st-"] {font-family:Tahoma,Arial,sans-serif;}
.stApp {background:#f8f6f1;color:#202b29;}
[data-testid="stMainBlockContainer"] {max-width:1040px;padding-top:2.4rem;padding-bottom:2rem;}
[data-testid="stSidebar"] {background:#152e29;color:#f6f0df;direction:rtl;border-left:1px solid #bfa66a;}
[data-testid="stSidebar"] p,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3 {color:#f6f0df;}
[data-testid="stSidebar"] .stButton button {background:#254039;color:#f5eedc;border:1px solid #5a6c56;}
[data-testid="stSidebar"] .stDownloadButton button {background:#bfa66a;color:#152e29;border:0;}
[data-testid="stChatMessage"] {direction:rtl;text-align:right;background:white;border:1px solid #e9e3d5;border-radius:18px;padding:1.25rem;margin-bottom:1rem;}
[data-testid="stChatMessage"] p {line-height:2;}
[data-testid="stChatInput"] {direction:rtl;border:1px solid #bfa66a;border-radius:14px;}
.hero {direction:rtl;text-align:right;padding:28px 32px;background:#152e29;border-radius:22px;color:#fff9e9;margin-bottom:20px;}
.hero .eyebrow {color:#d7bf82;font-size:13px;letter-spacing:1px;}
.hero h1 {color:#fff9e9;font-size:36px;font-weight:800;margin:12px 0;}
.hero p {color:#d7ded6;line-height:1.9;font-size:15px;margin:0;}
.badge {display:inline-block;border:1px solid #65735a;border-radius:30px;padding:5px 13px;font-size:11px;color:#d9ccaa;margin-top:18px;}
.section-label {direction:rtl;text-align:right;font-weight:700;font-size:14px;margin:20px 0 12px;color:#58645b;}
.side-brand {font-size:42px;font-weight:800;color:#d6bd80;margin-top:24px;}
.side-en {font-size:11px;letter-spacing:4px;color:#b4c2b6;margin-bottom:30px;}
.side-note {border-top:1px solid #496058;margin-top:28px;padding-top:20px;font-size:12px;color:#b7c5bb;line-height:2;}
.stButton button {border-radius:12px;border:1px solid #dfd7c3;background:#fffdf7;color:#294238;min-height:48px;}
.stButton button:hover {border-color:#a58b4e;color:#152e29;}
header {background:transparent!important;}
</style>""", unsafe_allow_html=True)

try:
    data = load_knowledge_base(Path(__file__).with_name("knowledge_base.json"))
except (OSError, ValueError):
    st.error("تعذر تحميل قاعدة المعرفة. يرجى التحقق من الملف وتنسيقه.")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.markdown('<div class="side-brand">الأريج ✦</div><div class="side-en">AL AREEJ · PERFUMES</div>', unsafe_allow_html=True)
    st.markdown("### مساعد المتجر")
    st.write("كل ما تحتاج معرفته عن عطورنا، في محادثة واحدة.")
    st.divider()
    st.markdown("**مواضيع يمكنني مساعدتك بها**")
    st.write("الشحن والتوصيل · الأسعار · الدفع\n\nالاستبدال والاسترجاع · اختيار العطور")
    if st.button("＋ محادثة جديدة", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    if st.session_state.messages:
        transcript = "\n\n".join(("أنت" if m["role"] == "user" else "المساعد") + ": " + m["content"] for m in st.session_state.messages)
        st.download_button("↓ حفظ المحادثة", transcript, "alareej-chat.txt", "text/plain", use_container_width=True)
    st.markdown('<div class="side-note">نموذج أعمال تجريبي · بيانات متجر توضيحية<br>إجابات من قاعدة معرفة محلية، دون اتصال بنموذج لغوي.<br>تُحفظ المحادثة في جلسة المتصفح الحالية فقط.</div>', unsafe_allow_html=True)

st.markdown('<div class="hero"><div class="eyebrow">تجربة خدمة عملاء عربية</div><h1>أهلاً بك في عالم الأريج ✦</h1><p>عطر يعبّر عنك، ومساعدة أقرب إليك.<br>اسأل عن منتجاتنا أو الشحن أو سياسات المتجر، وسأساعدك بالمعلومات المتاحة.</p><span class="badge">● متاح للتجربة &nbsp; | &nbsp; قاعدة معرفة المتجر</span></div>', unsafe_allow_html=True)
st.markdown('<div class="section-label">ابدأ بسؤال سريع</div>', unsafe_allow_html=True)
examples = [("🚚 الشحن والتوصيل", "هل يوجد توصيل للمحافظات؟"), ("↩ الاستبدال والاسترجاع", "ما هي سياسة الاسترجاع والاستبدال؟"), ("✦ اختيار عطرك", "كيف أختار العطر المناسب لفصل الصيف؟")]
selected = None
for column, (label, question) in zip(st.columns(3), examples):
    if column.button(label, use_container_width=True):
        selected = question
st.markdown('<div class="section-label">محادثتك مع مساعد الأريج</div>', unsafe_allow_html=True)
with st.chat_message("assistant", avatar="🤖"):
    st.write("أهلاً بك! أنا مساعد الأريج. كيف يمكنني مساعدتك اليوم؟")
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🤖" if message["role"] == "assistant" else "👤"):
        st.write(message["content"])

prompt = st.chat_input("اكتب سؤالك هنا…", max_chars=1000)
if selected or prompt:
    question = selected or prompt
    answer = answer_from_knowledge_base(question, data["knowledge_base"])
    st.session_state.messages.extend([{"role": "user", "content": question}, {"role": "assistant", "content": answer}])
    st.rerun()
