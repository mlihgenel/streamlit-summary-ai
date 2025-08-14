import streamlit as st
from datetime import datetime, date
import logging
from utils import load_topics, save_topics
from model import get_response

logging.basicConfig(
    filename="app.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s -%(filename)s",
    level=logging.INFO
)

# sayfa ayarlamalarının yapılması
st.set_page_config(
    page_title="Summary.AI | Summarize your daily work",
    layout="wide",
    page_icon="https://www.transparentpng.com/download/s/oH5wPR-escritura-creativaacru-sticos.png"
)    
# ============================================================================================================

# ============================ Initilize Session State ==================================================
try:
    if "topics" not in st.session_state:
        st.session_state["topics"] = load_topics()
        
    st.session_state.setdefault("topics", [])
    st.session_state.setdefault("input_text", "")
    st.session_state.setdefault("summary", "")
    st.session_state.setdefault("keywords","")
    st.session_state.setdefault("feedback_suggestion","")
    st.session_state.setdefault("title", "")
    logging.info("Session State'ler tanımlandı")
except:
    logging.warning("Sessin State tanımlamasında hata oluştu")
# ============================================================================================================

import streamlit as st

st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Anton&display=swap" rel="stylesheet">
    <style>
        .custom-title {
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Anton', sans-serif;
            font-size: 70px;
            font-weight: bold;
            gap: 10px; /* yazı ile logo arası boşluk */
            
            
        }
        .custom-title img {
            height: 120px; /* logonun boyutu */
            margin-bottom: 20px
        }
        .aciklama {
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Lato', sans-serif;
            font-size: 20px;
            color: #8C8989
        }
    </style>
    <div class="custom-title">
        <img src="https://www.transparentpng.com/download/s/oH5wPR-escritura-creativaacru-sticos.png" alt="logo">
        Summary.AI
    </div>
    <div class="aciklama">
        Summarize your day, get instant feedback, and discover key insights — powered by AI
    </div>
""", unsafe_allow_html=True)


# ================================== Konu Ekleme-Silme Fonksiyonları ===========================================
def delete_topic(key_to_remove):
    new_topics = []
    for topics in st.session_state.topics:
        if (topics["text"], topics["created"]) != key_to_remove:
            new_topics.append(topics)
            
    st.session_state.topics = new_topics
    save_topics(st.session_state.topics)  
    logging.info("Silme işlemi gerçekleşti")
    
def add_topic():
        txt = st.session_state.get("input_text", "").strip()
        if not txt:
            st.warning("Please enter the text to summarize.")
            return

        with st.spinner("Analyzing text... Creating summary and feedback.", show_time=True):
            response = get_response(txt)

        if response:
            now = datetime.now()
            new_topic = {
                "text": txt,
                "created": now.strftime("%Y-%m-%d, %H:%M"),
                "date": now.strftime("%Y-%m-%d"),
                "title": response.get("title", "Başlık oluşturulamadı"),
                "summary": response.get("summary", "Özet oluşturulamadı"),
                "keywords": response.get("keywords", "Anahtar kelimeler oluşturulamadı"),
                "feedback_suggestion": response.get("feedback_suggestion", "Öneri oluşturulamadı")
            }
            
            st.session_state.topics.append(new_topic)
            save_topics(st.session_state.topics)
            
            # Update session state for immediate display
            st.session_state.title = new_topic["title"]
            st.session_state.summary = new_topic["summary"]
            st.session_state.keywords = new_topic["keywords"]
            st.session_state.feedback_suggestion = new_topic["feedback_suggestion"]
            
            st.session_state.input_text = ""  # Clear input field
            logging.info("Analiz başarıyla tamamlandı ve kaydedildi.")
            
        else:
            logging.error("Modelden analiz alınamadı.")
            st.error("Could not get analysis from the model. Please try again.")
# ==============================================================================================================
left, right = st.columns([1, 3], gap="medium", border=True)
        
with left:
    st.header("History")
    selected_date = st.date_input("Select a date", value=date.today())
    search_keyword = st.text_input("Search with keyword")
    "---"
    all_topics = st.session_state.get("topics", [])

    # ===================== Sol Bölüm Filtreleme Kısmı ====================================   
    filtered = []
    for topic in all_topics:
        date_match = topic.get("date") == selected_date.isoformat()

        keyword_match = True
        if search_keyword:
            keywords_str = topic.get("keywords", "")
            if keywords_str:
                keywords_list = []
                for keyword in keywords_str.split(","):
                    if keyword.strip():
                        keywords_list.append(keyword.strip().lower())
                keyword_match = any(search_keyword.lower() in kw for kw in keywords_list)
            else:
                keyword_match = False

        if date_match and keyword_match:
            filtered.append(topic)
    
    topics = filtered[::-1]
    
    if not topics:
        st.info("No topics found for this date.")
    # =====================================================================================
    # ======================== Sol Bölüm Listelemele Kısmı ================================
    else:                
        for i, item in enumerate(topics):
            
            if not item["title"]:
                left_title = "Başlık Bulunamadı..."
            else:
                left_title = item["title"]
            with st.expander(f"{left_title}\n\n {item['created']}", expanded=False): 
                st.markdown("### Summary:")
                st.write(item.get("summary",""))
                st.markdown("#### Feedback and Suggestion:\n")
                st.write(item.get("feedback_suggestion",""))
                keywords_list = []
                try:
                    for keyoword in item.get("keywords", "").split(","):
                        if keyoword.strip():
                            keywords_list.append(keyoword.strip())
                    for kw in keywords_list:
                        st.badge(kw)
                    
                except:
                    logging.warning("Anahtar kelimeler oluşturulamadı")
                
                try:
                    st.button("Delete",
                            key=f"del_{i}",
                            on_click=delete_topic,
                            args=((item["text"], item["created"]),)
                            )
                except:
                    logging.warning(f"Silme işlemi gerçekleştirilemedi")
                    
# =========================================================================================


with right:
    st.header("Today I Learned:")
    text = st.text_area("",height=150, key="input_text")
    
    button = st.button("Summarize", on_click=add_topic, width=150) 
       
    "---"
    if st.session_state:
        st.subheader("Last Summary:")
        st.markdown(st.session_state.summary)
        st.subheader("Feedback and Suggestion")
        st.markdown(st.session_state.feedback_suggestion)
        st.subheader("Keywords: ")
        keywords_list = []
        try:
            for keyword in st.session_state.keywords.split(","):
                if keyword.strip():
                    keywords_list.append(keyword.strip())
            for kw in keywords_list:
                st.badge(kw)
            
        except:
            logging.warning("Anahtar kelimeler oluşturulamadı")
    else:
        st.caption("There is no summary yet")

# ==============================================
  