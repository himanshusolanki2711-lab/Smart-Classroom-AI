import streamlit as st
import time
import os
import io
from datetime import datetime

# --- 1. INITIALIZATION (Errors rokne ke liye) ---
if 'student_db' not in st.session_state:
    st.session_state.student_db = {
        "Himanshu": {
            "interest": "Python, Video Editing", 
            "achievements": ["Top 10", "Code Master"], 
            "bio": "B.Tech 2nd Year Student", 
            "attendance": "85%",
            "marks": {"Maths": 88, "Physics": 75, "CS": 92}
        },
        "Aryan": {
            "interest": "Java, Math", 
            "achievements": ["Mathlete"], 
            "bio": "Software Dev enthusiast", 
            "attendance": "90%",
            "marks": {"Maths": 95, "Physics": 82, "CS": 80}
        }
    }

if 'notices' not in st.session_state:
    st.session_state.notices = [
        {"msg": "Final Exams starting from May 15th.", "by": "Admin", "time": time.ctime()}
    ]

if 'admin_pass' not in st.session_state:
    st.session_state.admin_pass = "bhai123"

# Directory for PYQ files
pyq_dir = "uploaded_pyqs"
if not os.path.exists(pyq_dir):
    os.makedirs(pyq_dir)

# --- 2. SETUP & THEME ---
st.set_page_config(page_title="AI Omni-University ERP", layout="wide")

st.markdown("""
    <style>
    .top-10-tag { background-color: #f1c40f; color: #2c3e50; padding: 3px 10px; border-radius: 15px; font-weight: bold; margin-right: 5px;}
    .marks-card { background-color: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 5px solid #2ecc71; margin-bottom: 10px;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. GEMINI AI CONFIG ---
API_KEY = "AIzaSyCN6WgtYUCjtMSFcza8zWumohMw-mH399w" 

try:
    import google.generativeai as genai
    genai.configure(api_key=API_KEY)
    model_text = genai.GenerativeModel('gemini-1.5-flash')
    ai_status = "Connected ✅"
except Exception:
    ai_status = "Key Error ⚠️"

# --- 4. SIDEBAR ---
st.sidebar.title("🛡️ AI Guardian Suite")
user_role = st.sidebar.selectbox("Select User Role", ["Student", "Teacher", "Admin"])

# Admin/Teacher Access check
access_granted = False
if user_role in ["Teacher", "Admin"]:
    pwd = st.sidebar.text_input("Enter Admin Password", type="password")
    if pwd == st.session_state.admin_pass:
        access_granted = True
    else:
        st.sidebar.warning("Password required for access.")
else:
    access_granted = True

menu = ["🏠 Dashboard", "📢 Notice Board", "🎙️ Audio Notes", "📚 Study Hub (PYQs)", "📊 Marks Management", "👤 Admin & Profiles"]
choice = st.sidebar.radio("Navigate", menu)

# --- 5. APP MAIN LOGIC ---

if choice == "🏠 Dashboard":
    st.title(f"Welcome, {user_role} Dashboard")
    col1, col2, col3 = st.columns(3)
    
    # Personal info for student
    if user_role == "Student":
        student_name = "Himanshu" # Defaulting for demo
        data = st.session_state.student_db[student_name]
        col1.metric("My Attendance", data["attendance"])
        col2.metric("Total Subjects", len(data["marks"]))
        
        st.subheader("My Academic Record")
        for sub, score in data["marks"].items():
            st.markdown(f"<div class='marks-card'><b>{sub}:</b> {score}/100</div>", unsafe_allow_html=True)
    else:
        col1.metric("Total Students", len(st.session_state.student_db))
        col2.metric("Active Notices", len(st.session_state.notices))
    
    col3.metric("AI Engine", ai_status)

elif choice == "📢 Notice Board":
    st.header("Official Notice Board")
    if access_granted and user_role != "Student":
        with st.expander("➕ Post New Notice"):
            msg = st.text_area("Content")
            if st.button("Publish"):
                st.session_state.notices.append({"msg": msg, "by": user_role, "time": time.ctime()})
                st.rerun()
    for n in reversed(st.session_state.notices):
        st.info(f"**{n['by']}** ({n['time']}):\n{n['msg']}")

elif choice == "🎙️ Audio Notes":
    st.header("🎙️ Class Notes Transcriber")
    transcript = st.text_area("Type or Paste lecture transcript:", "The topic today is Thermodynamics...")
    if st.button("Generate AI Summary"):
        if ai_status == "Connected ✅":
            with st.spinner("AI Processing..."):
                res = model_text.generate_content(f"Summarize this lecture transcript in clear points: {transcript}")
                st.write(res.text)
        else:
            st.error("API Key missing or invalid.")

elif choice == "📚 Study Hub (PYQs)":
    st.header("PYQ Repository")
    files = os.listdir(pyq_dir)
    
    if access_granted and user_role != "Student":
        up = st.file_uploader("Upload PDF Paper")
        if up and st.button("Upload"):
            with open(os.path.join(pyq_dir, up.name), "wb") as f:
                f.write(up.getbuffer())
            st.success("File Saved!")
            st.rerun()
            
    if not files:
        st.info("Repository is empty.")
    for f in files:
        with open(os.path.join(pyq_dir, f), "rb") as file_data:
            st.download_button(label=f"📥 Download {f}", data=file_data, file_name=f, key=f)

elif choice == "📊 Marks Management":
    st.header("Academic Performance Management")
    if not access_granted or user_role == "Student":
        st.error("Students cannot edit marks. Check Dashboard for your results.")
    else:
        student = st.selectbox("Select Student to Update", list(st.session_state.student_db.keys()))
        col1, col2 = st.columns(2)
        subject = col1.text_input("Subject Name")
        score = col2.number_input("Marks (0-100)", 0, 100, 75)
        
        if st.button("Update Marks"):
            st.session_state.student_db[student]["marks"][subject] = score
            st.success(f"Updated {subject} for {student}!")

elif choice == "👤 Admin & Profiles":
    if not access_granted:
        st.error("Restricted Area")
    else:
        st.header("User Directory")
        student = st.selectbox("View Profile", list(st.session_state.student_db.keys()))
        s_data = st.session_state.student_db[student]
        
        st.subheader(f"Name: {student}")
        st.write(f"**Bio:** {s_data['bio']}")
        tags = "".join([f'<span class="top-10-tag">{t}</span> ' for t in s_data['achievements']])
        st.markdown(tags, unsafe_allow_html=True)
        
        if user_role == "Admin":
            new_tag = st.text_input("Add Achievement")
            if st.button("Add"):
                st.session_state.student_db[student]['achievements'].append(new_tag)
                st.rerun()
