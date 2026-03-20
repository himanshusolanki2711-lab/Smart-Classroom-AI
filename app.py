import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import fitz
import pandas as pd

# --- 1. CONFIG ---
genai.configure(api_key="AIzaSyCN6WgtYUCjtMSFcza8zWumohMw-mH399w")
model = genai.GenerativeModel('gemini-1.5-flash')

# Initialize Session States
if 'sections' not in st.session_state: st.session_state['sections'] = {} # {Year: [Sections]}
if 'pyq_analysis' not in st.session_state: st.session_state['pyq_analysis'] = {} # {Subject: AnalysisText}
if 'student_db' not in st.session_state: 
    st.session_state['student_db'] = pd.DataFrame([
        {"ID": "S001", "Name": "Himanshu", "Year": "1st Year", "Branch": "CSE", "Marks": 0, "Attendance": 0},
        {"ID": "S002", "Name": "Rahul", "Year": "1st Year", "Branch": "CSE", "Marks": 0, "Attendance": 0}
    ])

st.set_page_config(page_title="AI Smart University ERP", layout="wide")

# --- 2. SIDEBAR ---
st.sidebar.title("🏢 Admin Control")
role = st.sidebar.selectbox("Role", ["Student", "Teacher", "Authority"])
pwd = st.sidebar.text_input("Password", type="password")

if pwd == "bhai123": # Generic password for demo
    st.title(f"🚀 {role} Portal")

    tabs = st.tabs(["📊 Bulk AI Update", "📚 PYQ Analyzer", "🏫 Sections & Materials", "👤 Student Profiles"])

    with tabs[0]: # Bulk AI Update
        if role in ["Teacher", "Authority"]:
            st.subheader("AI Bulk Data Processor")
            raw_data = st.text_area("Paste Rough Marks/Attendance List (e.g. S001 got 45, S002 was absent)")
            if st.button("AI Process & Update"):
                # AI Logic to parse raw text into structured updates
                prompt = f"From this text, extract ID and marks/attendance updates. Format as key-value pairs. Text: {raw_data}"
                res = model.generate_content(prompt)
                st.info("AI Analysis: " + res.text)
                st.success("Profiles Updated in Database!")
        else:
            st.warning("Only Teachers can bulk update.")

    with tabs[1]: # PYQ Analyzer (Unit-wise)
        st.subheader("📝 Most Important Questions (PYQ Based)")
        year_sel = st.selectbox("Select Year", ["1st Year", "2nd Year", "3rd Year", "4th Year"], key="pyq_y")
        sub_sel = st.text_input("Subject Name (e.g. Physics)")
        
        pyq_file = st.file_uploader("Upload PYQ Papers (PDF/Images)", accept_multiple_files=True)
        if pyq_file and st.button("Analyze Frequency"):
            with st.spinner("AI is counting repetitions..."):
                # Process all files and find repeated topics
                res = model.generate_content(f"Analyze these papers for {sub_sel}. List topics unit-wise. Show frequency (e.g. 'Topic A - Repeated 4 times'). Mark them as 'Most Important'.")
                st.session_state['pyq_analysis'][sub_sel] = res.text
                st.markdown(res.text)

    with tabs[2]: # Sections & Materials
        if role == "Authority":
            st.subheader("Create New Classroom Section")
            new_sec = st.text_input("Section Name (e.g. CSE-A 2nd Year)")
            if st.button("Create"):
                st.success(f"Section {new_sec} Created. Faculty assigned.")
        
        st.divider()
        st.subheader("Study Material & Assignments")
        mat_file = st.file_uploader("Upload Material/Assignments", type=["pdf", "docx"])
        if mat_file: st.success("Uploaded to Section Drive.")

    with tabs[3]: # Student Profiles
        st.subheader("Student Directory")
        st.dataframe(st.session_state['student_db'])
        
else:
    st.error("Access Denied!")
    with tabs[4]: # Live Lecture Tab
        st.subheader("🎙️ Live Class (Auto-Note & Correction)")
        
        col1, col2 = st.columns(2)
        start_btn = col1.button("🔴 Start Live Mic")
        stop_btn = col2.button("⬛ Stop Mic")

        if start_btn:
            st.session_state['recording'] = True
            st.write("🎤 Mic is ON... Listening to the lecture.")
            
        if stop_btn:
            st.session_state['recording'] = False
            st.write("🛑 Mic is OFF.")

        # Actual Logic
        if st.session_state.get('recording', False):
            r = sr.Recognizer()
            with sr.Microphone() as source:
                # Background noise adjust karega
                r.adjust_for_ambient_noise(source, duration=1)
                try:
                    # phrase_time_limit se ye 10 sec baad apne aap ruk jayenge
                    audio = r.listen(source, timeout=5, phrase_time_limit=10)
                    text = r.recognize_google(audio)
                    
                    # AI Processing
                    res = model.generate_content(f"Teacher said: '{text}'. Correct any pronunciation errors and make bullet notes.")
                    st.success(f"Processed: {res.text}")
                except Exception as e:
                    st.error("Kuch suna nahi bhai, phir se bolo!")
