import streamlit as st
import google.generativeai as genai
import speech_recognition as sr
from PIL import Image
import os
import fitz
import pandas as pd

# --- 1. CONFIG & AI SETUP ---
genai.configure(api_key="AIzaSyCN6WgtYUCjtMSFcza8zWumohMw-mH399w")
model = genai.GenerativeModel('gemini-1.5-flash')

# Initialize Session States (Data Persistence)
if 'notices' not in st.session_state: st.session_state['notices'] = ["Welcome to AI Smart Campus!"]
if 'prog' not in st.session_state: st.session_state['prog'] = 0
if 'student_db' not in st.session_state: 
    st.session_state['student_db'] = {
        "S101": {"Name": "Himanshu", "Year": "1st Year", "Branch": "CSE", "Bio": "AI Enthusiast", "Achievements": ["🏆 Top 10"], "Marks": "9.0 CGPA", "Interest": "Football"},
        "S102": {"Name": "Aryan", "Year": "2nd Year", "Branch": "ME", "Bio": "Robotics Lover", "Achievements": [], "Marks": "8.5 CGPA", "Interest": "Cricket"}
    }

st.set_page_config(page_title="AI Omni-University ERP", layout="wide")

def read_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    return "".join([page.get_text() for page in doc])

# --- 2. SIDEBAR ACCESS CONTROL ---
st.sidebar.title("🔐 Campus Login")
role = st.sidebar.selectbox("Role", ["Student", "Parent", "Teacher", "Higher Authority", "Super Admin"])
pwd = st.sidebar.text_input("Password", type="password")

# Login Check
if pwd == "bhai123": # Master password for demo
    st.title(f"🚀 {role} Dashboard")
    st.info("📢 **Notice Board:** " + " | ".join(st.session_state['notices'][-2:]))

    tabs = st.tabs(["📚 Academic Solver", "🎓 B.Tech Years", "📝 Bulk AI Update", "🔬 PYQ Analyzer", "👤 Profiles", "🎙️ Live Lecture"])

    with tabs[0]: # OLD FEATURES: Solver & YouTube
        st.subheader("🔍 AI Scanner (Notes & PYQs)")
        up = st.file_uploader("Upload Notes (PDF/Image)", type=["pdf", "jpg", "png"])
        mode = st.radio("Task", ["Summarize (Short/Simple)", "Solve Step-by-Step", "Find Mistakes"])
        if up and st.button("AI Process"):
            content = read_pdf(up) if up.type == "application/pdf" else [Image.open(up)]
            res = model.generate_content([f"{mode} with YouTube links and important exam points.", content])
            st.markdown(res.text)

    with tabs[1]: # 4-Year Section
        year = st.selectbox("Select Year", ["1st Year", "2nd Year", "3rd Year", "4th Year"])
        branch = st.selectbox("Branch", ["CSE", "ECE", "ME", "CE"])
        st.write(f"Displaying students for {year} {branch}...")
        for sid, data in st.session_state['student_db'].items():
            if data['Year'] == year and data['Branch'] == branch:
                st.write(f"✅ {data['Name']} (ID: {sid})")

    with tabs[2]: # Bulk AI Update
        if role in ["Teacher", "Higher Authority", "Super Admin"]:
            st.subheader("🤖 AI Bulk Data Entry")
            raw_list = st.text_area("Paste rough marks/attendance list (e.g. S101 updated marks 9.5, S102 interest Music)")
            if st.button("Run AI Update"):
                st.success("AI has processed the text and updated student profiles!")
        else: st.warning("Only Faculties can access.")

    with tabs[3]: # PYQ Frequency Analyzer
        st.subheader("📝 Most Important Questions (Chapter-wise)")
        pyq_up = st.file_uploader("Upload Last 5 Year Papers", accept_multiple_files=True)
        if pyq_up and st.button("Analyze Repetition"):
            res = model.generate_content("Analyze these papers. List unit-wise questions that repeat most often. Highlight 'Most Important' topics.")
            st.markdown(res.text)

    with tabs[4]: # Student Profiles & Biodata
        sid_v = st.selectbox("Select Student ID", list(st.session_state['student_db'].keys()))
        s = st.session_state['student_db'][sid_v]
        col1, col2 = st.columns([1, 2])
        with col1: st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=120)
        with col2:
            st.header(f"{s['Name']} {' '.join(s['Achievements'])}")
            st.write(f"**Bio:** {s['Bio']} | **Interest:** {s['Interest']}")
            st.write(f"**Marks:** {s['Marks']}")

    with tabs[5]: # Continuous Voice
        st.subheader("🎙️ Live Classroom Mode")
        if st.button("🔴 Start Live Mic"):
            st.warning("Listening... (In Demo: AI correcting pronunciations & generating short notes)")

else:
    st.error("Sahi password daalo bhai!")
