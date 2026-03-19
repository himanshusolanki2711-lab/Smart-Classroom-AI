import streamlit as st
import google.generativeai as genai
import speech_recognition as sr
from PIL import Image
from fpdf import FPDF
import os
import io

# --- 1. AUTO MODEL CONFIG ---
genai.configure(api_key="AIzaSyCN6WgtYUCjtMSFcza8zWumohMw-mH399w")

def get_best_model():
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        if 'models/gemini-1.5-flash' in models: return genai.GenerativeModel('models/gemini-1.5-flash')
        return genai.GenerativeModel(models[0])
    except: return genai.GenerativeModel('gemini-pro')

model = get_best_model()

# --- 2. FOLDER SETUP ---
DB_FOLDER = "PYQ_Database"
if not os.path.exists(DB_FOLDER): os.makedirs(DB_FOLDER)

# --- 3. PDF HELPER ---
def create_pdf(text, title):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt=title, ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=11)
    clean_text = text.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, txt=clean_text)
    return pdf.output(dest='S').encode('latin-1')

st.set_page_config(page_title="Ultimate AI Smart Classroom", layout="wide")

# --- 4. SIDEBAR: AUTH & TEACHER CONTROL ---
st.sidebar.title("🔐 Control & Access")
if 'master_pass' not in st.session_state: st.session_state['master_pass'] = "admin123"

new_pass = st.sidebar.text_input("Teacher: Set/Change Password", value=st.session_state['master_pass'], type="password")
if st.sidebar.button("Update Password"):
    st.session_state['master_pass'] = new_pass
    st.sidebar.success("Password Updated!")

st.sidebar.divider()
selected_class = st.sidebar.selectbox("Class", ["B.Tech 1st Year", "B.Tech 2nd Year", "Class 12", "Class 10"])
selected_subject = st.sidebar.text_input("Subject", "Physics / CS / Maths")
entered_pass = st.sidebar.text_input("Enter Classroom Password", type="password")

# --- 5. MAIN LOGIC (AUTHENTICATED) ---
if entered_pass == st.session_state['master_pass']:
    st.title(f"🚀 {selected_subject} - Smart Learning Dashboard")
    
    # Syllabus Tracker
    st.subheader("📊 Syllabus Completion Bar")
    prog = st.slider("Kitna syllabus ho gaya? (%)", 0, 100, 40)
    st.progress(prog/100)
    st.info(f"Target completion: **Lagbhag {int((100-prog)*1.3)} din bache hain.**")

    tab1, tab2, tab3, tab4 = st.tabs(["🎙️ Audio Lecture", "📷 Notes & PYQ Scanner", "📂 Study Archive", "📉 Authority Audit"])

    # ENHANCED PROMPT FOR 3 SECTIONS + YOUTUBE
    master_prompt = f"""
    Act as a professional tutor for {selected_class} {selected_subject}. 
    Analyze the input and provide exactly these 4 things:
    
    1. SECTION A: SHORT & CRISP (Main bullet points for quick revision).
    2. SECTION B: SIMPLE EXPLANATION (Easy to understand version for students).
    3. SECTION C: EXAM POINT (Identify likely PYQs/important questions from this topic with their frequency if visible).
    4. YOUTUBE RECOMMENDATION: Provide 1-2 specific 'One Shot' video titles and search links (YouTube) that are short, time-saving, and have high reviews for this specific topic.
    
    Input: 
    """

    with tab1:
        st.subheader("Live Lecture Recording")
        if st.button("🔴 Start Mic"):
            r = sr.Recognizer()
            with sr.Microphone() as source:
                st.info("Listening... Speak clearly.")
                audio = r.listen(source)
            try:
                text = r.recognize_google(audio)
                st.success(f"Transcribed: {text}")
                res = model.generate_content(f"{master_prompt} {text}")
                st.session_state['last_content'] = res.text
                st.markdown(res.text)
            except Exception as e: st.error(f"Error: {e}")

    with tab2:
        st.subheader("Scan & Summarize Notes / Papers")
        uploaded_files = st.file_uploader("Upload Notes or PYQ Images", type=["jpg", "png", "jpeg"], accept_multiple_files=True)
        
        if uploaded_files and st.button("Analyze & Summarize"):
            imgs = [Image.open(f) for f in uploaded_files]
            with st.spinner("AI is scanning, identifying PYQs and finding YouTube videos..."):
                res = model.generate_content([master_prompt] + imgs)
                st.session_state['last_content'] = res.text
                st.markdown(res.text)

    with tab3:
        st.subheader("📂 Digital Resource Library")
        db_files = os.listdir(DB_FOLDER)
        if db_files:
            for f_name in db_files:
                c1, c2 = st.columns([3, 1])
                c1.write(f"📄 {f_name}")
                with open(os.path.join(DB_FOLDER, f_name), "rb") as f:
                    c2.download_button("Download", f, file_name=f_name, key=f_name)
        else: st.warning("PYQ_Database folder mein files daalein.")

    with tab4:
        st.subheader("👨‍🏫 Teacher Quality & Parent Review")
        if 'last_content' in st.session_state:
            audit = model.generate_content(f"Review these notes for teaching effectiveness and clarity: {st.session_state['last_content']}")
            st.success("AI Analysis for Parents/Authorities:")
            st.write(audit.text)
        else: st.info("Pehle notes ya lecture scan karein.")

    # PDF DOWNLOAD
    if 'last_content' in st.session_state:
        st.divider()
        pdf_bytes = create_pdf(st.session_state['last_content'], f"{selected_subject} Smart Pack")
        st.download_button("📥 Download This Session as PDF", pdf_bytes, "Smart_Notes.pdf")

else:
    st.warning("Password daal kar access karein.")
    st.image("https://img.icons8.com/bubbles/200/000000/lock.png")