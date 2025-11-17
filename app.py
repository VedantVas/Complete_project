import streamlit as st
import requests
import os

# -------------------- Optional Imports --------------------
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    from PIL import Image
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False

try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

# -------------------- PAGE CONFIG --------------------
st.set_page_config(page_title="🌐Welcome to Auralis", layout="wide")

# -------------------- CUSTOM CSS --------------------
page_bg = """
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #E3FDFD, #CBF1F5, #A6E3E9, #71C9CE);
}
h1, h2, h3, h4, h5, h6 {
    color: #0A3D62 !important;
}
p, span, div {
    color: #0F172A !important;
}
.stButton>button {
    background-color: #0F4C75;
    font-weight: bold;
    border-radius: 10px;
    padding: 0.7em 1.5em;
    border: none;
}
.stButton>button:hover {
    background-color: #3282B8;
}
.stButton>button p,
.stButton>button span,
.stButton>button div {
    color: #FFFFFF !important;
}
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    background-color: #0F4C75 !important;
    color: #FFFFFF !important;
    border-radius: 10px !important;
    border: 2px solid #1B6B93 !important;
    font-weight: bold;
}
[data-testid="stTextInput"] input::placeholder,
[data-testid="stTextArea"] textarea::placeholder {
    color: #E3FDFD !important;
}
[data-baseweb="select"] span { color: #FFFFFF !important; }
.news-card {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
    padding: 16px;
    margin: 10px 0px;
    border-radius: 12px;
    box-shadow: 0px 6px 14px rgba(0,0,0,0.18);
}
.news-card h4 { color: #0F4C75 !important; font-weight: bold; }
.news-card a {
    color: #3282B8 !important;
    font-weight: 700;
    text-decoration: none;
}
.news-card a:hover { text-decoration: underline; }
.follow-btn {
    background-color: #0F4C75;
    color: #FFFFFF !important;
    border-radius: 8px;
    padding: 0.5em 1em;
    text-align: center;
    font-weight: bold;
    width: 100%;
    display: inline-block;
    text-decoration: none;
}
.follow-btn:hover { background-color: #3282B8 !important; }
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# -------------------- SESSION STATE --------------------
if "page" not in st.session_state:
    st.session_state.page = "home"
if "gemini_api_key" not in st.session_state:
    st.session_state.gemini_api_key = ""
if "news_api_key" not in st.session_state:
    st.session_state.news_api_key = ""

# -------------------- HEADER --------------------
st.markdown("<h1 style='text-align:center;'>🌐 Auralis</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:18px;'>Your AI Chatbot, Dictionary & News — All in One Place!</p>", unsafe_allow_html=True)
st.write("")

# -------------------- NAVIGATION --------------------
col1, col2, col3, col4 = st.columns([1,1,1,1])
with col1:
    if st.button("🤖 AI Chatbot"):
        st.session_state.page = "chatbot"
with col2:
    if st.button("📖 Dictionary"):
        st.session_state.page = "dictionary"
with col3:
    if st.button("📰 News Reader"):
        st.session_state.page = "news"
with col4:
    if st.button("ℹ️ About"):
        st.session_state.page = "about"

st.write("---")

# -------------------- HOME PAGE --------------------
if st.session_state.page == "home":
    st.subheader("✨ Welcome to Auralis!")
    st.write("Your smart multi-utility platform for AI chat, dictionary, and news — all combined in one place.")

# -------------------- CHATBOT SECTION --------------------
elif st.session_state.page == "chatbot":
    st.subheader("🤖 AI Chatbot - Ask Anything!")

    if not GEMINI_AVAILABLE:
        st.error("Install using: pip install google-generativeai")

    st.session_state.gemini_api_key = st.text_input("Enter Gemini API Key", type="password")

    uploaded_file = st.file_uploader("Upload txt, pdf, docx or image", type=["txt","pdf","docx","jpg","jpeg","png"])
    extracted_text = ""

    if uploaded_file:
        try:
            if uploaded_file.name.endswith(".txt"):
                extracted_text = uploaded_file.read().decode("utf-8")
            elif uploaded_file.name.endswith(".docx") and DOCX_AVAILABLE:
                extracted_text = "\n".join([p.text for p in docx.Document(uploaded_file).paragraphs])
            elif uploaded_file.name.endswith(".pdf") and PYMUPDF_AVAILABLE:
                pdf = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                extracted_text = "".join([p.get_text() for p in pdf])
            elif uploaded_file.type.startswith("image/") and PYTESSERACT_AVAILABLE:
                extracted_text = pytesseract.image_to_string(Image.open(uploaded_file))
        except:
            st.error("❌ Error reading file")
        else:
            st.text_area("Extracted Text:", extracted_text, height=200)

    question = st.text_input("Ask your question:")

    if st.button("ASK"):
        if not st.session_state.gemini_api_key:
            st.error("Please enter API key!")
        elif not question:
            st.warning("Type a question")
        else:
            try:
                genai.configure(api_key=st.session_state.gemini_api_key)
                model = genai.GenerativeModel("gemini-pro")

                prompt = question if not extracted_text else f"Use context:\n{extracted_text}\n\nQ:{question}"

                response = model.generate_content(prompt)
                st.success(response.text)
            except:
                st.error("AI request failed")

# -------------------- DICTIONARY SECTION --------------------
elif st.session_state.page == "dictionary":
    st.subheader("📖 Dictionary")
    word = st.text_input("Enter word:")

    if word:
        res = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}")
        if res.status_code == 200:
            meaning = res.json()[0]["meanings"][0]["definitions"][0]["definition"]
            st.success(meaning)
        else:
            st.error("Word not found")

# -------------------- NEWS SECTION --------------------
elif st.session_state.page == "news":
    st.subheader("📰 News Reader")
    st.session_state.news_api_key = st.text_input("Enter NewsAPI Key", type="password")

    categories = ["Technology","Sports","Business","Entertainment","Health","Science"]
    category = st.selectbox("Category", categories)
    query = st.text_input("Search topic (optional)")

    def get_news(api, category, query):
        params = {"apiKey": api, "language": "en", "pageSize": 8}
        url = "https://newsapi.org/v2/everything" if query else "https://newsapi.org/v2/top-headlines"
        if query: params["q"] = query
        else: params["category"] = category.lower()
        return requests.get(url, params=params).json().get("articles", [])

    if st.session_state.news_api_key:
        articles = get_news(st.session_state.news_api_key, category, query)
        for a in articles:
            st.markdown(f"""
                <div class="news-card">
                    <h4>{a.get("title")}</h4>
                    <p>{a.get("description")}</p>
                    <a href="{a.get("url")}" target="_blank">Read more</a>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Enter API key to load news")

# -------------------- ABOUT SECTION --------------------
elif st.session_state.page == "about":
    st.subheader("ℹ️ About Auralis")

    st.markdown("""
    ### 🚀 Project Overview  
    **Auralis** is a smart multi-utility digital platform providing **AI Chatbot, Dictionary & Latest News** in one place to reduce digital switching and improve productivity.

    ### 🛠️ Tech Stack  
    - Python  
    - Streamlit  
    - Google Gemini API  
    - Dictionary API  
    - NewsAPI  
    - OCR Support (optional files)

    ### 👨‍💻 Project Created By  
    **▪ Vedant Vashishtha**  
    **▪ Raj Vishwakarma**  
    **▪ Abhay Rajak**

    ### 🎯 Vision  
    To develop a **smart integrated platform** eliminating dependency on multiple apps for productivity, learning, and awareness.

    ### 📌 Features  
    ✔ Smart AI Chatting  
    ✔ Live News Reading  
    ✔ Dictionary with Meaning & Pronunciation  
    ✔ File/Text Extraction Support  

    """)

# -------------------- FOOTER --------------------
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Made with ❤️ by Team Auralis</p>", unsafe_allow_html=True)
