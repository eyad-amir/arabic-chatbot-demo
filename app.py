import streamlit as st
import google.generativeai as genai

# Safely fetch API Key from Streamlit Secrets or fallback for local testing
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = "YOUR_LOCAL_API_KEY_HERE" # Fallback for local testing

genai.configure(api_key=api_key)

# 2. Load your knowledge base
with open('knowledge_base.json', 'r', encoding='utf-8') as file:
    kb_data = file.read()

# 3. Give the AI its strict instructions
system_instruction = f"""
You are a helpful customer service assistant for Al-Areej Perfumes. 
You MUST answer users in Arabic.
ONLY use the information in this knowledge base to answer questions:
{kb_data}
If the user asks something not in the knowledge base, say exactly: 'عذراً، ليس لدي معلومات حول هذا الأمر. يرجى التواصل مع خدمة العملاء.'
"""

model = genai.GenerativeModel(
    model_name="gemini-3.6-flash",
    system_instruction=system_instruction
)

# 4. Streamlit UI Setup
st.title("🤖 عطور الأريج - خدمة العملاء")
st.write("أهلاً بك! كيف يمكنني مساعدتك اليوم؟")

# 5. Initialize chat history in Streamlit memory
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat()

# Display previous chat messages
for message in st.session_state.chat_session.history:
    role = "user" if message.role == "user" else "assistant"
    with st.chat_message(role):
        st.markdown(message.parts[0].text)

# 6. Chat input box
if user_input := st.chat_input("اكتب سؤالك هنا..."):
    # Show user message on screen
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Get bot response and show it
    with st.chat_message("assistant"):
        response = st.session_state.chat_session.send_message(user_input)
        st.markdown(response.text)