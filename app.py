import streamlit as st
import requests
import PyPDF2

# 🔑 Replace with your OpenRouter API key
import os
API_KEY = os.getenv("API_KEY")

# 🌐 API URL
URL = "https://openrouter.ai/api/v1/chat/completions"

# 🎨 Page setup
st.set_page_config(page_title="PDF Chatbot", page_icon="📄")

st.title("📄 AI PDF Chatbot")
st.caption("Ask questions from your document")

# 🧹 Sidebar
with st.sidebar:
    st.header("Options")
    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []

# 📄 Load PDF (only once)
@st.cache_data
def load_pdf():
    with open("notes.pdf", "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text

pdf_text = load_pdf()

# 🧠 Initialize memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# 🤖 API call with memory
def get_response(messages):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "PDF Chatbot"
    }

    data = {
        "model": "arcee-ai/trinity-large-thinking:free",
        "messages": messages
    }

    try:
        response = requests.post(URL, headers=headers, json=data)
        result = response.json()

        if "choices" in result:
            return result["choices"][0]["message"]["content"]
        else:
            return f"⚠️ Error: {result}"

    except Exception as e:
        return f"⚠️ Exception: {str(e)}"

# 💬 Show chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ✍️ Input
user_input = st.chat_input("Ask something from PDF...")

if user_input:
    # Save user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    # 📄 Add PDF context
    context = pdf_text[:4000]

    user_prompt = f"""
Answer ONLY from this document:

{context}

User Question: {user_input}
"""

    # 🧠 Combine memory + current question
    temp_messages = st.session_state.messages.copy()
    temp_messages.append({"role": "user", "content": user_prompt})

    # Limit memory (optional but recommended)
    temp_messages = temp_messages[-6:]

    # 🤖 Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            reply = get_response(temp_messages)
            st.markdown(reply)

    # Save response
    st.session_state.messages.append({"role": "assistant", "content": reply})
