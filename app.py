import streamlit as st
import time
import os
import io
from datetime import datetime

# --- 1. INITIALIZATION (Sabse pehle errors ko roko) ---
if 'student_db' not in st.session_state:
    st.session_state.student_db = {
        "Himanshu": {"interest": "Python, Video Editing", "achievements": ["Top 10", "Code Master"], "bio": "B.Tech 2nd Year Student", "attendance": "85%"},
        "Aryan": {"interest": "Java, Math", "achievements": ["Mathlete"], "bio": "Software Dev enthusiast", "attendance": "90%"}
    }

if 'notices' not in st.session_state:
    st.session_state.notices = [
        {"msg": "Final Exams starting from May 15th.", "by": "Admin", "time": time.ctime()}
    ]

if 'pyq_files_db' not in st.session_state:
    st.session_state.pyq_files_db = []

if 'pdf_summaries' not in st.session_state:
    st.session_state.pdf_summaries = {}

if 'admin_pass' not in st.session_state:
    st.session_state.admin_pass = "bhai123"

# Directory for files
pyq_dir = "uploaded_pyqs"
if not os.path.exists(pyq_dir):
    os.makedirs(pyq_dir)

# --- 2. SETUP & THEME ---
st.set_page_config(page_title="AI Omni-University ERP", layout="wide")

# Custom Styling
st.markdown("""
    <style>
    .top-10-tag { background-color: #f1c40f; color: #2c3e50; padding: 3px 10px; border-radius: 15px; font-weight: bold; margin-right: 5px;}
    .code-star-tag { background-color: #3498db; color: white; padding: 3px 10px; border-radius: 15px; font-weight: bold; margin-right: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. GEMINI AI CONFIG ---
# BHAI YAHAN APNI KEY DAAL DE BAS
API_KEY = "AIzaSyCN6WgtYUCjtMSFcza8zWumohMw-mH399w" 

try:
    import google.generativeai as genai
    genai.configure(AIzaSyCN6WgtYUCjtMSFcza8zWumohMw-mH399w)
    model_text = genai.GenerativeModel('gemini-1.5-flash')
    ai_status = "Connected ✅"
except Exception:
    ai_status = "Key Error ⚠️"

# --- 4. SIDEBAR ---
st.sidebar.title("🛡️ AI Guardian Suite")
user_role = st.sidebar.selectbox("Select User Role", ["Student", "Teacher", "Admin"])

access_granted = False
if user_role in ["Teacher", "Admin"]:
    pwd = st.sidebar.text_input("Enter Admin Password", type="password")
    if pwd == st.session_state.admin_pass:
        access_granted = True
    else:
        st.sidebar.warning("Password required for Teacher/Admin")
else:
    access_granted = True

menu = ["🏠 Dashboard", "📢 Notice Board", "🎙️ Audio Notes", "📚 Study Hub (PYQs)", "🔍 AI Advanced Tools", "👤 Admin & Profiles"]
choice = st.sidebar.radio("Navigate", menu)

# --- 5. APP MAIN LOGIC ---

if choice == "🏠 Dashboard":
    st.title(f"Welcome, {user_role}")
    col1, col2, col3 = st.columns(3)
    col1.metric("Attendance", "85%" if user_role == "Student" else "N/A")
    col2.metric("New Notices", len(st.session_state.notices))
    col3.metric("AI Status", ai_status)
    st.info(f"Latest: {st.session_state.notices[-1]['msg']}")

elif choice == "📢 Notice Board":
    st.header("Official Notice Board")
    if user_role != "Student" and access_granted:
        with st.expander("➕ Post New Notice"):
            msg = st.text_area("Content")
            if st.button("Publish"):
                st.session_state.notices.append({"msg": msg, "by": user_role, "time": time.ctime()})
                st.rerun()
    for n in reversed(st.session_state.notices):
        st.info(f"**{n['by']}** ({n['time']}):\n{n['msg']}")

elif choice == "🎙️ Audio Notes":
    st.header("🎙️ Class Notes Transcriber")
    listen_time = st.number_input("Listening time (sec):", 10, 300, 60)
    transcript = st.text_area("Past transcribed text or type here:", "Hello, this is a lecture on Material Science...")
    
    if st.button("Organize with AI") and ai_status == "Connected ✅":
        with st.spinner("AI is working..."):
            res = model_text.generate_content(f"Format these notes: {transcript}")
            st.markdown(res.text)

elif choice == "📚 Study Hub (PYQs)":
    st.header("Resource & Study Hub")
    # Folder scan logic
    files_in_folder = os.listdir(pyq_dir)
    
    if user_role != "Student" and access_granted:
        up = st.file_uploader("Upload PYQ Paper")
        if up and st.button("Save to Repository"):
            with open(os.path.join(pyq_dir, up.name), "wb") as f:
                f.write(up.getbuffer())
            st.success("File Saved!")
            st.rerun()
    
    st.subheader("Available Papers:")
    if not files_in_folder:
        st.info("No files in repository.")
    else:
        for f_name in files_in_folder:
            with open(os.path.join(pyq_dir, f_name), "rb") as f_data:
                st.download_button(label=f"📥 Download {f_name}", data=f_data, file_name=f_name)

elif choice == "🔍 AI Advanced Tools":
    st.header("Advanced AI Academic Tools")
    tool = st.radio("Tool:", ["PDF Summary", "Assignment Feedback"])
    file = st.file_uploader("Upload PDF", type=['pdf'])
    if file and st.button("Analyze with AI"):
        st.success("Analysis starting... (Requires Gemini integration)")

elif choice == "👤 Admin & Profiles":
    if not access_granted and user_role != "Student":
        st.error("Access Denied")
    else:
        st.header("Student Directory")
        student = st.selectbox("Select Student", list(st.session_state.student_db.keys()))
        s_data = st.session_state.student_db[student]
        
        st.subheader(f"Name: {student}")
        st.write(f"**Bio:** {s_data['bio']}")
        st.write(f"**Attendance:** {s_data['attendance']}")
        
        # Tags display
        tags = "".join([f'<span class="top-10-tag">{t}</span>' for t in s_data['achievements']])
        st.markdown(tags, unsafe_allow_html=True)
        
        if user_role == "Admin" and access_granted:
            new_tag = st.text_input("Add Tag")
            if st.button("Apply"):
                st.session_state.student_db[student]['achievements'].append(new_tag)
                st.rerun()
