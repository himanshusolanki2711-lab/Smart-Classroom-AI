import streamlit as st
import time
import os
import io
import google.generativeai as genai
from datetime import datetime

# Mic recorder try-except taaki crash na ho
try:
    from streamlit_mic_recorder import mic_recorder
    mic_recorder_installed = True
except ImportError:
    mic_recorder_installed = False

# --- 1. INITIALIZATION ---
if 'student_db' not in st.session_state:
    st.session_state.student_db = {
        "Himanshu": {"interest": "Python, Video Editing", "achievements": ["Top 10"], "bio": "B.Tech Student", "attendance": "85%", "marks": {}},
        "Aryan": {"interest": "Java", "achievements": ["Mathlete"], "bio": "Dev", "attendance": "90%", "marks": {}}
    }

if 'notices' not in st.session_state:
    st.session_state.notices = [{"msg": "Welcome!", "by": "Admin", "time": time.ctime()}]

if 'admin_pass' not in st.session_state:
    st.session_state.admin_pass = "bhai123"

pyq_dir = "uploaded_pyqs"
if not os.path.exists(pyq_dir):
    os.makedirs(pyq_dir)

# --- 2. SETUP & AI CONFIG ---
st.set_page_config(page_title="AI Omni-University ERP", layout="wide")

API_KEY = "AIzaSyAeKWcg5XA_ajlz5GNkNiSt9JzvMy6hEas" # Teri key
try:
    genai.configure(api_key=API_KEY)
    model_text = genai.GenerativeModel('gemini-1.5-flash')
    ai_status = "Connected ✅"
except:
    ai_status = "Key Error ⚠️"

# --- 3. SIDEBAR ---
st.sidebar.title("🛡️ AI Guardian Suite")
user_role = st.sidebar.selectbox("Select Role", ["Student", "Teacher", "Admin"])

access_granted = False
if user_role != "Student":
    pwd = st.sidebar.text_input("Admin Pass", type="password")
    if pwd == st.session_state.admin_pass: access_granted = True
else:
    access_granted = True

menu = ["🏠 Dashboard", "📢 Notice Board", "🎙️ Audio Notes Converter", "📚 Study Hub (PYQs)", "📊 Marks Management", "👤 Admin & Profiles"]
choice = st.sidebar.radio("Navigate", menu)

# --- 4. FEATURE LOGIC ---

if choice == "🏠 Dashboard":
    st.title(f"🚀 {user_role} Dashboard")
    col1, col2, col3 = st.columns(3)
    col1.metric("Attendance", "85%")
    col2.metric("Notices", len(st.session_state.notices))
    col3.metric("AI Engine", ai_status)

elif choice == "🎙️ Audio Notes Converter":
    st.header("🎙️ Class Notes Transcriber")
    listen_time = st.slider("Set listening time (seconds):", 10, 300, 60)
    
    col_a, col_b = st.columns(2)
    with col_a:
        if mic_recorder_installed:
            audio = mic_recorder(start_prompt="Record Audio", stop_prompt="Stop Recording")
        else:
            st.error("pip install streamlit-mic-recorder karo pehle!")
    
    with col_b:
        transcript = st.text_area("Transcription / Input:", "Hello, this is a lecture note...")
        if st.button("Organize with AI"):
            if ai_status == "Connected ✅":
                res = model_text.generate_content(f"Summarize this in bullet points: {transcript}")
                st.write(res.text)

elif choice == "📚 Study Hub (PYQs)":
    st.header("Resource & Study Hub")
    # Repository Logic: Folder scan
    files = os.listdir(pyq_dir)
    
    if user_role != "Student" and access_granted:
        up = st.file_uploader("Upload PYQ Paper")
        if up and st.button("Save to Repository"):
            with open(os.path.join(pyq_dir, up.name), "wb") as f:
                f.write(up.getbuffer())
            st.success("File added to repository!")
            st.rerun()

    st.subheader("Available PYQs in Repository:")
    if not files:
        st.info("No files found.")
    for f_name in files:
        with open(os.path.join(pyq_dir, f_name), "rb") as f_data:
            st.download_button(label=f"📥 Download {f_name}", data=f_data, file_name=f_name)

elif choice == "📊 Marks Management":
    st.header("Marks Entry")
    if user_role == "Student": st.error("Access Denied")
    elif access_granted:
        name = st.selectbox("Student", list(st.session_state.student_db.keys()))
        sub = st.text_input("Subject")
        score = st.number_input("Marks", 0, 100)
        if st.button("Update"):
            st.session_state.student_db[name]["marks"][sub] = score
            st.success("Updated!")

elif choice == "👤 Admin & Profiles":
    if access_granted:
        st.header("Student Profiles")
        student = st.selectbox("Select Student", list(st.session_state.student_db.keys()))
        st.write(st.session_state.student_db[student])
