import streamlit as st
import google.generativeai as genai
import speech_recognition as sr
from PIL import Image
import os

# --- 1. CORE CONFIG ---
genai.configure(api_key="AIzaSyCN6WgtYUCjtMSFcza8zWumohMw-mH399w")
model = genai.GenerativeModel('gemini-1.5-flash')

# Initialize States
if 'prog' not in st.session_state: st.session_state['prog'] = 0
if 'admin_pass' not in st.session_state: st.session_state['admin_pass'] = "bhai123" # Tera personal pass
if 'teacher_pass' not in st.session_state: st.session_state['teacher_pass'] = "sir456" # Teachers ke liye
if 'syllabus_data' not in st.session_state: st.session_state['syllabus_data'] = "No Syllabus Uploaded"

st.set_page_config(page_title="AI Pro Classroom", layout="wide")

# --- 2. SIDEBAR (ACCESS CONTROL) ---
st.sidebar.title("🔐 Multi-User Login")
role = st.sidebar.selectbox("Select Role", ["Student", "Teacher", "Super Admin (You)"])
input_pass = st.sidebar.text_input("Enter Password", type="password")

# --- 3. SUPER ADMIN SECTION (Sirf tere liye) ---
if role == "Super Admin (You)" and input_pass == st.session_state['admin_pass']:
    st.sidebar.success("Welcome Bhai!")
    new_tp = st.sidebar.text_input("Change Teacher Password")
    if st.sidebar.button("Update Teacher Pass"):
        st.session_state['teacher_pass'] = new_tp
        st.sidebar.success("Updated!")

# --- 4. TEACHER SECTION ---
elif role == "Teacher" and input_pass == st.session_state['teacher_pass']:
    st.title("👨‍🏫 Teacher Intelligence Panel")
    st.subheader("Upload Syllabus to Track Progress")
    syll_file = st.file_uploader("Upload Syllabus Image/Notes", type=["jpg","png","jpeg"], key="syll")
    if syll_file:
        res = model.generate_content(["Extract all topic names from this syllabus and summarize them briefly.", Image.open(syll_file)])
        st.session_state['syllabus_data'] = res.text
        st.success("Syllabus Scanned & Saved!")

# --- 5. STUDENT/MAIN DASHBOARD ---
elif role == "Student" or (role == "Teacher" and input_pass == st.session_state['teacher_pass']):
    st.title("📚 AI Smart Classroom Dashboard")
    
    # Progress Tracker
    st.subheader(f"📊 Syllabus Progress: {st.session_state['prog']}%")
    st.progress(st.session_state['prog']/100)

    t1, t2, t3, t4 = st.tabs(["🔍 Doubt Solver & Notes", "🎙️ Live Lecture", "📂 PYQ Library", "📝 Short Audit"])

    with t1:
        st.subheader("Upload any Question or Note")
        up_file = st.file_uploader("Scan Question/Note", type=["jpg","png","jpeg"])
        mode = st.radio("What do you want?", ["Summarize & PYQs", "Solve Step-by-Step", "Check My Mistakes"])
        
        if up_file and st.button("AI Action"):
            img = Image.open(up_file)
            if mode == "Solve Step-by-Step":
                prompt = "Explain this question with steps and methods clearly."
            elif mode == "Check My Mistakes":
                prompt = "Look at my solved answer in this image. Find any mistakes and tell me the correct way."
            else:
                prompt = f"Summarize this topic. Also, compare it with this syllabus: {st.session_state['syllabus_data']}. If topic matches syllabus, tell me. Give 3 sections: Short, Simple, PYQ and YouTube Link."
            
            res = model.generate_content([prompt, img])
            
            # Auto Syllabus Update Logic
            if mode == "Summarize & PYQs":
                st.session_state['prog'] = min(st.session_state['prog'] + 4, 100)
            
            st.markdown(res.text)

    with t2:
        if st.button("🔴 Record Lecture"):
            # (Purana Voice Logic yahan rahega)
            st.write("Listening... (Transcribing to Master Notes)")
    with t3:
        st.subheader("📂 Digital Archive (PYQs)")
        # GitHub pe upload ki gayi files yahan dikhengi
        files = [f for f in os.listdir('.') if f.endswith('.pdf') or f.endswith('.jpg')]
        if files:
            for f_name in files:
                col1, col2 = st.columns([3, 1])
                col1.write(f"📄 {f_name}")
                with open(f_name, "rb") as f:
                    col2.download_button("Download", f, file_name=f_name, key=f_name)
        else:
            st.warning("Abhi koi PYQ upload nahi kiya gaya hai. GitHub par PDFs upload karein!")
    with t4:
        st.subheader("Teacher Quality Audit (Short)")
        if up_file:
            audit = model.generate_content(f"Give a 2-line professional feedback on the clarity of these notes: {res.text if 'res' in locals() else ''}")
            st.info(audit.text)

else:
    st.warning("Please select role and enter correct password.")
