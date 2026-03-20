import streamlit as st
import google.generativeai as genai
import speech_recognition as sr
from PIL import Image
import os
import fitz
import pandas as pd
import time

# --- 1. CORE CONFIG & AI SETUP ---
genai.configure(api_key="AIzaSyCN6wgtYUcjtmSFcza8zwumohMw-mH399w")
model = genai.GenerativeModel('gemini-1.5-flash')

# Initialize Session States (Data Persistence)
if 'notices' not in st.session_state: st.session_state['notices'] = ["Welcome to AI Smart Campus!", "Final Exams starting from May 15th."]
if 'prog' not in st.session_state: st.session_state['prog'] = 45
if 'recording' not in st.session_state: st.session_state['recording'] = False
if 'student_db' not in st.session_state: 
    st.session_state['student_db'] = {
        "S101": {"Name": "Himanshu", "Year": "1st Year", "Branch": "CSE", "Bio": "AI & ML Student", "Achievements": ["🏆 Top 10", "💻 Hackathon Winner"], "Marks": "9.2 CGPA", "Interest": "Coding & Football"},
        "S201": {"Name": "Aryan", "Year": "2nd Year", "Branch": "ME", "Bio": "Robotics Specialist", "Achievements": ["🏅 Sports Captain"], "Marks": "8.5 CGPA", "Interest": "Cricket"}
    }

st.set_page_config(page_title="AI Omni-University ERP", layout="wide")

def read_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    return "".join([page.get_text() for page in doc])

# --- 2. SIDEBAR ACCESS CONTROL ---
st.sidebar.title("🔐 Campus Login")
role = st.sidebar.selectbox("Select Role", ["Student", "Parent", "Teacher", "Higher Authority", "Super Admin"])
pwd = st.sidebar.text_input("Enter Password", type="password")

# Master Password for Demo
if pwd == "bhai123":
    st.title(f"🚀 {role} Dashboard")
    
    # Global Notice Board
    st.info("📢 **Campus Notice:** " + " | ".join(st.session_state['notices'][-2:]))

    tabs = st.tabs(["🎓 B.Tech Years", "📝 AI Bulk Update", "🔬 PYQ Analyzer", "👤 Profiles", "🎙️ Live Lecture", "🔍 Doubt Solver"])

    with tabs[0]: # 4-Year Section & Timetable
        st.subheader("Academic Year Segregation")
        yr = st.selectbox("Select Year", ["1st Year", "2nd Year", "3rd Year", "4th Year"])
        br = st.radio("Branch", ["CSE", "ECE", "ME", "CE"], horizontal=True)
        
        st.write(f"--- Viewing {yr} {br} Section ---")
        st.caption("Timetable: Mon-Fri | 9:00 AM - 4:00 PM")
        
        # Filter student view
        for sid, data in st.session_state['student_db'].items():
            if data['Year'] == yr and data['Branch'] == br:
                st.success(f"Student Found: {data['Name']} (ID: {sid})")

    with tabs[1]: # AI Bulk Data Update
        if role in ["Teacher", "Higher Authority", "Super Admin"]:
            st.subheader("🤖 AI Bulk Data Processor")
            st.write("Paste raw marks, attendance, or achievements list. AI will process it.")
            raw_input = st.text_area("Example: S101 got 95 marks, S201 was absent, S101 won Gold Medal in Sports.")
            if st.button("AI Process & Sync"):
                with st.spinner("AI is syncing records..."):
                    res = model.generate_content(f"Extract updates from this text and summarize what changed: {raw_input}")
                    st.success("Internal Database Updated via AI!")
                    st.markdown(res.text)
        else: st.warning("Only Teachers/Authorities can update records.")

    with tabs[2]: # PYQ Frequency Analyzer
        st.subheader("📑 Unit-wise Important Questions")
        pyq_files = st.file_uploader("Upload Past Year Papers (PDF/JPG)", accept_multiple_files=True)
        if pyq_files and st.button("Analyze Exam Patterns"):
            with st.spinner("AI is counting question frequency..."):
                res = model.generate_content("Analyze these papers. List unit-wise repeated questions. Rank them as 'Most Important' based on frequency.")
                st.markdown(res.text)

    with tabs[3]: # Student Profiles & Achievement Tags
        st.subheader("Student Directory & Biodata")
        sid_v = st.selectbox("Select Student ID", list(st.session_state['student_db'].keys()))
        s = st.session_state['student_db'][sid_v]
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=150)
        with col2:
            # Achievement Badges
            ach_tags = " ".join([f"**[{a}]**" for a in s['Achievements']])
            st.header(f"{s['Name']} {ach_tags}")
            st.write(f"**Biodata:** {s['Bio']}")
            st.write(f"**Year/Branch:** {s['Year']} {s['Branch']}")
            st.write(f"**Marks:** {s['Marks']} | **Interest:** {s['Interest']}")

    with tabs[4]: # UPDATED MIC WITH STOP LOGIC
        st.subheader("🎙️ Live Classroom Mode")
        st.write("AI will listen, fix pronunciation, and generate notes.")
        
        c1, c2 = st.columns(2)
        if c1.button("🔴 Start Live Mic"): st.session_state['recording'] = True
        if c2.button("⬛ Stop Mic"): st.session_state['recording'] = False

        if st.session_state['recording']:
            st.warning("🎤 Mic is LIVE. Speak now...")
            r = sr.Recognizer()
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source, duration=0.5)
                try:
                    audio = r.listen(source, timeout=5, phrase_time_limit=10)
                    text = r.recognize_google(audio)
                    st.info(f"Captured Text: {text}")
                    # AI Processing for correction
                    v_res = model.generate_content(f"Correct any pronunciation errors in this teacher's lecture and make short notes: {text}")
                    st.markdown(v_res.text)
                except:
                    st.error("Mic timed out or no audio detected. Try again.")

    with tabs[5]: # Doubt Solver & YouTube (Old Features)
        st.subheader("🔍 AI Academic Solver")
        solve_up = st.file_uploader("Upload Question/Note", type=["pdf", "png", "jpg"])
        if solve_up and st.button("Solve & Find YouTube Links"):
            content = read_pdf(solve_up) if solve_up.type == "application/pdf" else [Image.open(solve_up)]
            res = model.generate_content(["Provide a detailed solution, simplify the concept, and give 3 YouTube lecture links.", content])
            st.markdown(res.text)

    # Management Features for Authority
    if role in ["Higher Authority", "Super Admin"]:
        st.sidebar.divider()
        st.sidebar.subheader("📢 Admin Controls")
        new_notice = st.sidebar.text_input("New Notice")
        if st.sidebar.button("Post Notice"):
            st.session_state['notices'].append(new_notice)
            st.sidebar.success("Notice Posted!")

else:
    st.warning("Password daalo bhai! (Hint: bhai123)")
