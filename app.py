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

# -------------------- CUSTOM CSS THEME --------------------
page_bg = """
<style>
/* Page Background Gradient */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #E3FDFD, #CBF1F5, #A6E3E9, #71C9CE);
}

/* Headings */
h1, h2, h3, h4, h5, h6 { color: #0A3D62 !important; }

/* Text */
p, span, div { color: #0F172A !important; }

/* Buttons */
.stButton>button {
    background-color: #0F4C75;
    border-radius: 10px;
    padding: 0.7em 1.5em;
    font-weight: bold;
    border: none;
}
.stButton>button:hover { background-color: #3282B8; }
.stButton>button * { color: #FFFFFF !important; }

/* Input & text areas */
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
[data-testid="stTextArea"] textarea::placeholder { color: #E3FDFD !important; }

/* NEWS CARD */
.news-card {
    background-color: white;
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 12px;
    box-shadow: 0px 6px 14px rgba(0, 0, 0, 0.18);
}
.news-card h4 { color: #0F4C75 !important; font-weight: bold; }
.news-card a {
    color: #3282B8 !important;
    font-weight: bold;
    text-decoration: none;
}
.news-card a:hover { text-decoration: underline; }

/* -------- FILE UPLOADER FIX -------- */
[data-testid="stFileUploader"] section {
    background-color: #FFFFFF !important;
    border: 2px solid #0F4C75 !important;
    border-radius: 10px !important;
    color: #0F172A !important;
}
[data-testid="stFileUploader"] div,
[data-testid="stFileUploader"] label {
    color: #0F172A !important;
}
[data-testid="stFileUploader"] section:hover {
    border-color: #3282B8 !important;
    background-color: #F5FBFF !important;
    box-shadow: 0px 4px 8px rgba(0,0,0,0.12);
}

</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)


# -------------------- SESSION --------------------
if "page" not in st.session_state:
    st.session_state.page = "home"

# -------------------- HEADER --------------------
st.markdown("<h1 style='text-align:center;'>🌐 Auralis</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Your AI Chatbot, Dictionary & News — All in One Place!</p>", unsafe_allow_html=True)
st.write("")

# -------------------- NAVIGATION --------------------
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("🤖 AI Chatbot"): st.session_state.page = "chatbot"
with col2:
    if st.button("📖 Dictionary"): st.session_state.page = "dictionary"
with col3:
    if st.button("📰 News Reader"): st.session_state.page = "news"
with col4:
    if st.button("ℹ️ About"): st.session_state.page = "about"

st.write("---")

# -------------------- HOME --------------------
if st.session_state.page == "home":
    st.subheader("✨ Welcome to Auralis")
    st.write("Your smart multi-utility platform for AI chat, dictionary, and news — all combined in one place.")


# -------------------- CHATBOT --------------------
elif st.session_state.page == "chatbot":
    st.subheader("🤖 AI Chatbot")

    if not GEMINI_AVAILABLE:
        st.error("Please install using: pip install google-generativeai")

    gemini_key = st.text_input("Enter Gemini API Key", type="password")

    uploaded = st.file_uploader("Upload text, PDF, DOCX, or image", type=["txt","pdf","docx","jpg","jpeg","png"])
    extracted = ""

    if uploaded:
        try:
            if uploaded.name.endswith(".txt"):
                extracted = uploaded.read().decode("utf-8")
            elif uploaded.name.endswith(".docx") and DOCX_AVAILABLE:
                extracted = "\n".join([p.text for p in docx.Document(uploaded).paragraphs])
            elif uploaded.name.endswith(".pdf") and PYMUPDF_AVAILABLE:
                pdf = fitz.open(stream=uploaded.read(), filetype="pdf")
                extracted = "".join([page.get_text() for page in pdf])
            elif uploaded.type.startswith("image/") and PYTESSERACT_AVAILABLE:
                extracted = pytesseract.image_to_string(Image.open(uploaded))
        except:
            st.error("Error extracting content")
        if extracted.strip():
            st.text_area("Extracted Text", extracted, height=200)

    user_query = st.text_input("Ask anything:")

    if st.button("ASK"):
        if not gemini_key:
            st.error("Missing API key")
        elif not user_query:
            st.warning("Ask a question")
        else:
            try:
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel("gemini-pro")
                prompt = user_query if not extracted else f"Use this context:\n{extracted}\n\nQ:{user_query}"
                reply = model.generate_content(prompt)
                st.success(reply.text)
            except:
                st.error("Gemini API Error")


# -------------------- DICTIONARY --------------------
elif st.session_state.page == "dictionary":
    st.subheader("📖 Dictionary")
    word = st.text_input("Enter word:").strip()

    if word:
        try:
            r = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}")
            if r.status_code == 200:
                data = r.json()[0]

                pronunciation, audio = "N/A", None
                for ph in data.get("phonetics", []):
                    if "text" in ph and pronunciation == "N/A":
                        pronunciation = ph["text"]
                    if "audio" in ph and ph["audio"]:
                        audio = ph["audio"]
                        break

                st.markdown(f"### 📌 {data['word'].capitalize()}")
                colA, colB = st.columns([2,1])
                with colA: st.info(f"🔊 Pronunciation: {pronunciation}")
                with colB:
                    if audio: st.audio(audio)

                main_meaning = data["meanings"][0]["definitions"][0]["definition"]
                st.success(main_meaning)

                example = data["meanings"][0]["definitions"][0].get("example")
                if example: st.write(f"✏️ *{example}*")

                with st.expander("More meanings"):
                    for m in data["meanings"]:
                        st.write(f"**{m['partOfSpeech']}**:")
                        for i, d in enumerate(m["definitions"][:3], start=1):
                            st.write(f"{i}. {d['definition']}")
                            if "example" in d:
                                st.write(f"   *{d['example']}*")
            else:
                st.error("No meaning found")
        except:
            st.error("Dictionary API not reachable")


# -------------------- NEWS (HARDCODED KEY) --------------------
elif st.session_state.page == "news":
    st.subheader("📰 News Reader")

    NEWS_API_KEY = "246661c7ea0d4f5b9b7c0a277e5e57aa"  # <-- Replace here

    if not NEWS_API_KEY:
        st.error("❌ Please add API key inside app.py")
    else:
        categories = ["Technology","Sports","Business","Entertainment","Health","Science"]
        cat = st.selectbox("Choose Category", categories)
        search = st.text_input("Search topic (optional)")

        def fetch(key, cat=None, q=None):
            params = {"apiKey": key, "language": "en", "pageSize": 8}
            url = "https://newsapi.org/v2/everything" if q else "https://newsapi.org/v2/top-headlines"
            if q: params["q"] = q
            else: params["category"] = cat.lower()
            return requests.get(url, params=params).json().get("articles",[])

        articles = fetch(NEWS_API_KEY, cat, search)

        if articles:
            for a in articles:
                st.markdown(f"""
                <div class="news-card">
                    <h4>{a.get("title")}</h4>
                    <p>{a.get("description")}</p>
                    <a href="{a.get("url")}" target="_blank">Read more</a>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("No articles found")


# -------------------- ABOUT --------------------
elif st.session_state.page == "about":
    st.subheader("ℹ️ About Auralis")
    st.markdown("""
    ### 🚀 Overview  
    Auralis unifies **AI Chat**, **Dictionary**, and **Live News** in one smart platform.

    ### 👨‍💻 Developers  
    - **Vedant Vashishtha**  
    - **Raj Vishwakarma**  
    - **Abhay Rajak**

    ### 🎯 Purpose  
    Reduce digital switching & improve learning and productivity.

    ### 🧩 Future Upgrades  
    - Voice mode  
    - Saved dictionary history  
    - User login system  
    """)


# -------------------- FOOTER --------------------
st.write("---")
st.markdown("<p style='text-align:center;'>Made with ❤️ by Team Auralis</p>", unsafe_allow_html=True)
