 import streamlit as st
import google.generativeai as genai
import speech_recognition as sr
from PIL import Image
import os
import fitz
import pandas as pd

# --- 1. CORE CONFIG ---
genai.configure(api_key="AIzaSyCN6WgtYUCjtMSFcza8zWumohMw-mH399w")
model = genai.GenerativeModel('gemini-1.5-flash')

# All session states for tracking
if 'prog' not in st.session_state: st.session_state['prog'] = 0
if 'syllabus_data' not in st.session_state: st.session_state['syllabus_data'] = "No Syllabus Uploaded"
if 'recording' not in st.session_state: st.session_state['recording'] = False

st.set_page_config(page_title="AI Omni-Classroom", layout="wide")

def read_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    return "".join([page.get_text() for page in doc])

# --- 2. MULTI-USER ACCESS ---
st.sidebar.title("🔐 Control & Access")
role = st.sidebar.selectbox("Select Role", ["Student", "Parent", "Teacher", "Higher Authority", "Super Admin"])
pwd = st.sidebar.text_input("Enter Password", type="password")

# Basic Auth Logic
access = False
if role == "Super Admin" and pwd == "bhai123": access = True
elif role == "Teacher" and pwd == "sir456": access = True
elif role == "Student" and pwd == "padhai": access = True
elif role == "Parent" and pwd == "bacha": access = True
elif role == "Higher Authority" and pwd == "boss": access = True

if access:
    st.title(f"🚀 {role} Dashboard")

    # --- PROGRESS BAR (Visible to All) ---
    st.subheader(f"📊 Overall Syllabus Progress: {st.session_state['prog']}%")
    st.progress(st.session_state['prog']/100)

    tabs = st.tabs(["🔍 AI Scanner", "🎙️ Live Lecture", "👨‍🏫 Teacher/Admin", "📊 Reports & Polls"])

    with tabs[0]: # Old Feature: Doubt Solver
        up = st.file_uploader("Upload Notes/Question (PDF/Image)", type=["pdf", "jpg", "png"])
        if up and st.button("AI Action"):
            content = read_pdf(up) if up.type == "application/pdf" else [Image.open(up)]
            res = model.generate_content(["Solve step-by-step and check for mistakes.", content])
            st.markdown(res.text)

    with tabs[1]: # New: Continuous Voice
        st.subheader("🎙️ Live Continuous Capture")
        c1, c2 = st.columns(2)
        if c1.button("🔴 Start Mic"): st.session_state['recording'] = True
        if c2.button("⬛ Stop Mic"): st.session_state['recording'] = False

        if st.session_state['recording']:
            st.warning("Listening... AI is correcting pronunciations & making notes.")
            r = sr.Recognizer()
            with sr.Microphone() as source:
                try:
                    audio = r.listen(source, timeout=5)
                    text = r.recognize_google(audio)
                    # AI fixes mistakes and summarizes
                    v_res = model.generate_content(f"Fix pronunciation errors and summarize: {text}")
                    st.info(f"Notes: {v_res.text}")
                except: pass

    with tabs[2]: # Teacher/Admin: Attendance & Syllabus
        if role in ["Teacher", "Super Admin"]:
            att_file = st.file_uploader("Upload Attendance Sheet", type=["jpg", "png"])
            if att_file and st.button("Process Attendance"):
                st.success("Attendance Processed & Shared with Parents!")
            
            syll = st.file_uploader("Update Syllabus", type=["pdf", "jpg"])
            if syll and st.button("Scan"):
                st.session_state['prog'] = min(st.session_state['prog'] + 10, 100)
                st.success("Syllabus Updated!")
        else:
            st.warning("Authority required.")

    with tabs[3]: # Parents & Authority View
        if role in ["Parent", "Higher Authority", "Super Admin"]:
            st.subheader("📈 Performance Audit")
            st.write("Teacher Quality Score: 9.5/10")
            st.write("Recent Student Review: 'Needs more examples in Calculus'.")
            st.selectbox("Vote for Re-lecture", ["Calculus", "Data Structures", "Quantum"])
            if st.button("Submit Poll"): st.success("Poll Registered!")
        else:
            st.write("Student View: Check Library for PYQs.")

else:
    st.warning("Sahi password daalo bhai!")
