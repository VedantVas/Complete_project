import streamlit as st
import requests
from PIL import Image
import pytesseract
import docx
import fitz  # PyMuPDF

# -------------------- PAGE CONFIG --------------------
st.set_page_config(page_title="🌐 Vedant's Smart Hub", layout="wide")

# -------------------- CUSTOM CSS (improved selectors) --------------------
page_bg = """
<style>
/* Background */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #E3FDFD, #CBF1F5, #A6E3E9, #71C9CE);
}

/* Headings */
h1, h2, h3, h4, h5, h6 {
    color: #0A3D62 !important;
}

/* Normal text */
p, span, div {
    color: #0F172A !important;
}

/* Buttons */
.stButton>button {
    background-color: #0F4C75;
    color: #FFFFFF !important;
    font-weight: bold;
    border-radius: 10px;
    padding: 0.7em 1.5em;
    border: none;
}
.stButton>button:hover {
    background-color: #3282B8;
}

/* Input and Dropdown Fields */
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

/* Dropdown text color */
[data-baseweb="select"] span {
    color: #FFFFFF !important;
}

/* News Cards — now light for better text visibility */
.news-card {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
    padding: 16px;
    margin: 10px 0px;
    border-radius: 12px;
    box-shadow: 0px 6px 14px rgba(0,0,0,0.18);
}
.news-card h4 {
    color: #0F4C75 !important;
    font-weight: bold;
}
.news-card p {
    color: #1E293B !important;
}
.news-card a {
    color: #3282B8 !important;
    font-weight: 700;
    text-decoration: none;
}
.news-card a:hover {
    text-decoration: underline;
}

/* Follow buttons */
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
.follow-btn:hover {
    background-color: #3282B8;
    color: #FFFFFF !important;
}
</style>
"""

st.markdown(page_bg, unsafe_allow_html=True)

# -------------------- SESSION STATE --------------------
if "page" not in st.session_state:
    st.session_state.page = "home"
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

# -------------------- HEADER --------------------
st.markdown("<h1 style='text-align:center;'>🌐 Vedant’s Smart Hub</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:18px;'>Your AI Chatbot, Dictionary & News — All in One Place!</p>", unsafe_allow_html=True)
st.write("")

# -------------------- NAVIGATION BUTTONS --------------------
col1, col2, col3 = st.columns([1,1,1])
with col1:
    if st.button("🤖 AI Chatbot"):
        st.session_state.page = "chatbot"
with col2:
    if st.button("📖 Dictionary"):
        st.session_state.page = "dictionary"
with col3:
    if st.button("📰 News Reader"):
        st.session_state.page = "news"

st.write("---")

# -------------------- CHATBOT SECTION --------------------
if st.session_state.page == "chatbot":
    st.subheader("🤖 AI Chatbot - Ask Anything!")

    st.session_state.api_key = st.text_input(
        "Enter your Gemini API Key (optional):",
        type="password",
        value=st.session_state.api_key,
        key="gemini_api_key_input"
    )

    st.write("Upload a file or image to extract text (optional):")
    uploaded_file = st.file_uploader("Choose a file (txt, pdf, docx, jpg, png)", 
                                     type=["txt", "pdf", "docx", "jpg", "jpeg", "png"],
                                     key="file_uploader_chatbot")

    extracted_text = ""
    if uploaded_file:
        try:
            if uploaded_file.name.endswith(".txt"):
                extracted_text = uploaded_file.read().decode("utf-8")
            elif uploaded_file.name.endswith(".docx"):
                doc = docx.Document(uploaded_file)
                extracted_text = "\n".join([p.text for p in doc.paragraphs])
            elif uploaded_file.name.endswith(".pdf"):
                pdf = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                for page in pdf:
                    extracted_text += page.get_text()
            elif uploaded_file.type.startswith("image/"):
                image = Image.open(uploaded_file)
                extracted_text = pytesseract.image_to_string(image)
        except Exception as e:
            st.error("Error extracting text: " + str(e))

        st.text_area("📄 Extracted Text:", extracted_text, height=200)

    user_question = st.text_input("💬 Ask me anything:", key="chat_user_question")
    if user_question:
        st.info("💡 You asked: " + user_question)
        if st.session_state.api_key:
            st.success("🔑 API Key added — Ready to connect with Gemini (feature coming soon!)")
        st.success("🤖 Response: This is a sample AI response. Connect Gemini API to enable real answers.")

# -------------------- DICTIONARY SECTION --------------------
elif st.session_state.page == "dictionary":
    st.subheader("📖 Dictionary App")
    word = st.text_input("🔍 Enter a word:", "", key="word_input").strip()

    if word:
        try:
            url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()[0]
                word_text = data["word"].capitalize()
                pronunciation = "N/A"
                audio_link = None
                phonetics = data.get("phonetics", [])
                for p in phonetics:
                    if "text" in p and pronunciation == "N/A":
                        pronunciation = p["text"]
                    if "audio" in p and p["audio"]:
                        audio_link = p["audio"]
                        break

                st.markdown(f"<h2 style='color:#0F4C75;'>📌 {word_text}</h2>", unsafe_allow_html=True)
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.info(f"🔊 Pronunciation: `{pronunciation}`")
                with col2:
                    if audio_link:
                        st.audio(audio_link, format="audio/mp3")

                meanings = data["meanings"]
                main_def = meanings[0]["definitions"][0]["definition"]
                example = meanings[0]["definitions"][0].get("example")

                st.success(f"💡 {main_def}")
                if example:
                    st.markdown(f"<p><b>✏️ Example:</b> {example}</p>", unsafe_allow_html=True)
                else:
                    st.info("No example available for this word.")

                with st.expander("📚 Show more meanings"):
                    for meaning in meanings:
                        part_of_speech = meaning["partOfSpeech"].capitalize()
                        st.markdown(f"<h4 style='color:#0F4C75;'>➡️ {part_of_speech}</h4>", unsafe_allow_html=True)
                        for idx, definition in enumerate(meaning["definitions"][:3], start=1):
                            st.write(f"{idx}. {definition['definition']}")
                            if "example" in definition:
                                st.markdown(f"<p>✏️ {definition['example']}</p>", unsafe_allow_html=True)
            else:
                st.error("❌ Word not found. Try another one.")
        except Exception as e:
            st.error("Error contacting dictionary API: " + str(e))

# -------------------- NEWS READER SECTION --------------------
elif st.session_state.page == "news":
    st.subheader("📰 News Reader")
    API_KEY = "246661c7ea0d4f5b9b7c0a277e5e57aa"
    BASE_URL = "https://newsapi.org/v2/top-headlines"

    # Use explicit keys so the inputs keep their values without resetting
    categories = ["Technology", "Sports", "Business", "Entertainment", "Health", "Science"]
    selected_category = st.selectbox("📂 Choose Category", categories, key="news_category_select")
    search_query = st.text_input("🔍 Or search for a topic:", key="news_search_input")

    def fetch_news(category=None, query=None):
        params = {
            "apiKey": API_KEY,
            "language": "en",
            "pageSize": 8
        }
        try:
            if query:
                params["q"] = query
                url = "https://newsapi.org/v2/everything"
            else:
                params["category"] = category.lower()
                url = BASE_URL
            r = requests.get(url, params=params, timeout=10)
            if r.status_code == 200:
                return r.json().get("articles", [])
            else:
                st.error("⚠ Failed to fetch news. Check API key or quota.")
                return []
        except Exception as e:
            st.error("⚠ Error fetching news: " + str(e))
            return []

    if search_query:
        articles = fetch_news(query=search_query)
        st.subheader(f"🔍 Results for '{search_query}'")
    else:
        articles = fetch_news(category=selected_category)
        st.subheader(f"📂 Top {selected_category} News")

    if articles:
        for article in articles:
            title = article.get("title", "No title")
            desc = article.get("description", "No description available.")
            url = article.get("url", "#")
            with st.container():
                st.markdown(
                    f"""
                    <div class="news-card">
                        <h4>{title}</h4>
                        <p>{desc}</p>
                        <a href="{url}" target="_blank">Read more 🔗</a>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    else:
        st.info("No news found. Try another search or category.")

# -------------------- FOOTER --------------------
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:16px;'>Made with ❤️ by Vedant Vashishtha</p>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown("<a href='https://www.linkedin.com/in/vedant-vashishtha-4933b3301/' target='_blank' class='follow-btn'>🔗 LinkedIn</a>", unsafe_allow_html=True)
with col2:
    st.markdown("<a href='https://github.com/VedantVas' target='_blank' class='follow-btn'>💻 GitHub</a>", unsafe_allow_html=True)
