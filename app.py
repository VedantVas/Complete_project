import streamlit as st
import requests
import os

# Optional imports
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

# Lottie animation loader
from streamlit_lottie import st_lottie

def load_lottie(url: str):
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()
    return None

# -------------------- PAGE CONFIG --------------------
st.set_page_config(page_title="Auralis | Nano-Core Intelligence System", layout="wide")

# -------------------- Fonts & Theme CSS (Iron Man HUD) --------------------
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700&family=Rajdhani:wght@300;400;600&display=swap" rel="stylesheet">
<style>

/* Global Font */
html, body, [class*="css"] {
    font-family: 'Rajdhani', sans-serif;
}

/* Background Nano-Tech Space */
[data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at 25% 25%, #003445 0%, #00121A 80%);
    background-attachment: fixed;
}

/* Grid Overlay */
[data-testid="stAppViewContainer"]::before {
    content: "";
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background-image: 
        linear-gradient(#00eaff1B 1px, transparent 1px),
        linear-gradient(90deg, #00eaff1B 1px, transparent 1px);
    background-size: 40px 40px;
    opacity: 0.4;
    pointer-events: none;
}

/* Scanline Effect */
[data-testid="stAppViewContainer"]::after {
    content: "";
    position: fixed;
    top:0; left:0;
    width:100%; height:100%;
    pointer-events:none;
    background: repeating-linear-gradient(
        to bottom,
        rgba(0, 255, 255, 0.05),
        rgba(0, 255, 255, 0.05) 2px,
        transparent 2px,
        transparent 4px
    );
    opacity: .14;
}

/* Titles */
.hud-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 40px;
    text-align: center;
    color: #00eaff;
    text-shadow: 0px 0px 25px #00eaff;
}

/* Sub Glowing Text */
.holo-text { color: #C7F9FF; opacity: 0.9; }

/* Animated Scan Divider */
.holo-divider {
    width: 90%;
    height: 2px;
    margin: auto;
    background: radial-gradient(circle, #00eaff 0%, transparent 75%);
    animation: pulse 2s infinite alternate;
}
@keyframes pulse { from {opacity:.4} to {opacity:1} }

/* Holographic Card */
.holo-card {
    border: 1px solid #00eaff88;
    border-radius: 16px;
    padding: 22px;
    background: rgba(0, 60, 75, 0.35);
    backdrop-filter: blur(8px);
    color: #d3faff;
    text-align: center;
    box-shadow: 0 0 12px #00eaff40 inset;
}

/* Buttons */
.stButton>button {
    background: rgba(0, 255, 255, 0.1);
    border: 1px solid #00eaffaa;
    color: #00eaff;
    font-weight: 600;
    padding: 0.6em 1.4em;
    border-radius: 40px;
    letter-spacing: 1px;
    transition: 0.25s;
    backdrop-filter: blur(4px);
}
.stButton>button:hover {
    box-shadow: 0 0 15px #00eaff;
    transform: scale(1.06);
}

/* Typewriter Nano-Text */
.typewriter {
    border-right: 3px solid #00eaff;
    white-space: nowrap;
    overflow: hidden;
    width: 0;
    animation: typing 3.2s steps(40, end) forwards, blink 0.8s infinite;
}
@keyframes typing { from {width: 0;} to {width: 100%;} }
@keyframes blink { 50% { border-color: transparent; } }

</style>
""", unsafe_allow_html=True)

# -------------------- SESSION STATE --------------------
if "page" not in st.session_state:
    st.session_state.page = "home"
if "gemini_api_key" not in st.session_state:
    st.session_state.gemini_api_key = ""
if "news_api_key" not in st.session_state:
    st.session_state.news_api_key = ""

# -------------------- NAVIGATION --------------------
st.markdown("<h1 class='hud-title'>AURALIS — NANO CORE INTELLIGENCE</h1>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

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
    if st.button("ℹ About"):
        st.session_state.page = "about"

st.markdown("<div class='holo-divider'></div><br>", unsafe_allow_html=True)

# -------------------- HOME PAGE (HUD) --------------------
if st.session_state.page == "home":
    orb_anim = load_lottie("https://lottie.host/94fea69e-0b69-45e1-99f4-83175f6634d6/HOlNQ7so6j.json")
    st_lottie(orb_anim, height=230, key="hud_orb", speed=1.15)
    
    st.markdown("""
        <div class="holo-card">
            <h3 style="color:#00eaff;">BLEEDING-EDGE NANO AI SYSTEM</h3>
            <p class="typewriter">Adaptive • Cognitive • Neural • Context-Aware Intelligence Channel Activated...</p>
        </div>
        <br>
        <div class="holo-divider"></div>
    """, unsafe_allow_html=True)


# -------------------- AI CHATBOT PAGE --------------------
elif st.session_state.page == "chatbot":
    st.subheader("🤖 Nano-Core AI Assistant")

    if not GEMINI_AVAILABLE:
        st.error("Install google-generativeai: pip install google-generativeai")

    st.session_state.gemini_api_key = st.text_input("Enter Gemini API Key", type="password")

    uploaded_file = st.file_uploader("Upload txt/pdf/docx/image (optional)", type=["txt", "pdf", "docx", "jpg", "jpeg", "png"])
    extracted_text = ""

    if uploaded_file:
        try:
            if uploaded_file.name.endswith(".txt"):
                extracted_text = uploaded_file.read().decode("utf-8")
            elif uploaded_file.name.endswith(".docx") and DOCX_AVAILABLE:
                extracted_text = "\n".join([p.text for p in docx.Document(uploaded_file).paragraphs])
            elif uploaded_file.name.endswith(".pdf") and PYMUPDF_AVAILABLE:
                pdf = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                extracted_text = "".join([page.get_text() for page in pdf])
            elif uploaded_file.type.startswith("image/") and PYTESSERACT_AVAILABLE:
                extracted_text = pytesseract.image_to_string(Image.open(uploaded_file))
        except:
            st.error("File extraction error")

        if extracted_text:
            st.text_area("Extracted Text:", extracted_text, height=200)

    query = st.text_input("Ask your question:")

    if st.button("ENGAGE AI"):
        if not st.session_state.gemini_api_key:
            st.error("API key missing")
        elif not query:
            st.error("Enter query")
        else:
            try:
                genai.configure(api_key=st.session_state.gemini_api_key)
                model = genai.GenerativeModel("gemini-pro")

                prompt = query if not extracted_text else f"Use context:\n{extracted_text}\n\nQuestion:{query}"

                with st.spinner("Processing like FRIDAY..."):
                    response = model.generate_content(prompt)
                    st.success("Response:")
                    st.markdown(response.text)
            except Exception as e:
                st.error(f"AI Error: {e}")


# -------------------- DICTIONARY PAGE --------------------
elif st.session_state.page == "dictionary":
    st.subheader("📖 HUD Dictionary")
    word = st.text_input("Enter a word:")

    if word:
        api = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        r = requests.get(api)

        if r.status_code == 200:
            data = r.json()[0]
            st.success(data["meanings"][0]["definitions"][0]["definition"])
        else:
            st.error("Word not found")


# -------------------- NEWS READER PAGE --------------------
elif st.session_state.page == "news":
    st.subheader("📰 Global Intelligence Channel")

    st.session_state.news_api_key = st.text_input("Enter NewsAPI Key", type="password")
    categories = ["Technology", "Sports", "Business", "Entertainment", "Health", "Science"]
    selected_category = st.selectbox("Select Category", categories)
    topic = st.text_input("Search Topic (optional)")

    def pull_news(api, cat=None, q=None):
        params = {"apiKey": api, "language": "en", "pageSize": 8}
        url = "https://newsapi.org/v2/everything" if q else "https://newsapi.org/v2/top-headlines"
        if q: params["q"] = q
        else: params["category"] = cat.lower()
        return requests.get(url, params=params).json().get("articles", [])

    if st.session_state.news_api_key:
        articles = pull_news(st.session_state.news_api_key, selected_category, topic)
        for a in articles:
            st.markdown(f"""
                <div class="holo-card">
                    <h4 style="color:#00eaff;">{a.get("title")}</h4>
                    <p class="holo-text">{a.get("description","No description")}</p>
                    <a href="{a.get("url")}" target="_blank" style="color:#00eaff;">READ →</a>
                </div><br>
            """, unsafe_allow_html=True)
    else:
        st.info("Enter API key to load live intelligence feed.")


# -------------------- ABOUT PAGE --------------------
elif st.session_state.page == "about":
    st.subheader("🧬 Project Information")

    st.markdown("""
    ### 👨‍💻 Developed By:
    | Name | Role |
    |------|------------------------------|
    | **Vedant Vashishtha** | Lead Dev & UI Architect |
    | **Raj Vishwakarma** | AI & Integration Specialist |
    | **Abhay Rajak** | Research Analyst |

    ### 🔭 Vision
    To build an all-in-one smart cognitive platform powered by AI and futuristic interface systems.

    ### 🧩 Tech Stack
    - Python  
    - Streamlit  
    - Google Gemini AI  
    - NewsAPI  
    - DictionaryAPI  
    - OCR: Tesseract / PyMuPDF / Docx  
    """)

# -------------------- FOOTER --------------------
st.markdown("<br><div class='holo-divider'></div>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#00eaff;'>🌀 Auralis Nano-Core | Powered by Stark-Grade Intelligence 🌀</p>", unsafe_allow_html=True)
