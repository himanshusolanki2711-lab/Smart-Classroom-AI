import streamlit as st
import os
from datetime import datetime
import google.generativeai as genai
import time

# --- 1. CONFIG & INITIALIZATION ---
st.set_page_config(page_title="AKTU AI Smart Campus", layout="wide")

BASE_DIR = "AKTU_University_Data"
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

# Professional Database Simulation
if 'user_db' not in st.session_state:
    st.session_state.user_db = {
        "Authority": "admin123", "Teacher": "teacher123", 
        "Student": "student123", "Parent": "parent123"
    }

if 'chats' not in st.session_state: st.session_state.chats = {} # {section_id: [messages]}
if 'reviews' not in st.session_state: st.session_state.reviews = [] # Anonymous logs

# Dummy Portals logic (10 Sections)
if 'aktu_portals' not in st.session_state:
    st.session_state.aktu_portals = {
        "AKTU_BTech_1st_Year_CS_A": {"pwd": "123", "yr": "1st Year", "sec": "CS-A", "course": "B.Tech"},
        "AKTU_BTech_1st_Year_ME_B": {"pwd": "123", "yr": "1st Year", "sec": "ME-B", "course": "B.Tech"},
        "AKTU_BTech_2nd_Year_CS_B": {"pwd": "123", "yr": "2nd Year", "sec": "CS-B", "course": "B.Tech"},
        "AKTU_BTech_2nd_Year_IT_A": {"pwd": "123", "yr": "2nd Year", "sec": "IT-A", "course": "B.Tech"},
        "AKTU_BTech_3rd_Year_CS_AI": {"pwd": "123", "yr": "3rd Year", "sec": "CS-AI", "course": "B.Tech"},
        "AKTU_BTech_3rd_Year_ECE_A": {"pwd": "123", "yr": "3rd Year", "sec": "ECE-A", "course": "B.Tech"},
        "AKTU_BTech_4th_Year_CS_DS": {"pwd": "123", "yr": "4th Year", "sec": "CS-DS", "course": "B.Tech"},
        "AKTU_BTech_4th_Year_Civil": {"pwd": "123", "yr": "4th Year", "sec": "Civil", "course": "B.Tech"},
        "AKTU_BTech_2nd_Year_EE": {"pwd": "123", "yr": "2nd Year", "sec": "EE", "course": "B.Tech"},
        "AKTU_BTech_1st_Year_BT": {"pwd": "123", "yr": "1st Year", "sec": "BT", "course": "B.Tech"}
    }
    
    # Create Dummy Folders & Files
    dummy_subjects = ["Maths", "Python", "Data_Structures", "Microprocessor"]
    today = datetime.now().strftime("%Y-%m-%d")
    for p_id, info in st.session_state.aktu_portals.items():
        for sub in dummy_subjects:
            path = os.path.join(BASE_DIR, "BTech", info['yr'], info['sec'], sub, today)
            if not os.path.exists(path):
                os.makedirs(path)
                with open(os.path.join(path, f"Lecture_Notes_{sub}.txt"), "w") as f:
                    f.write(f"Sample notes for {sub} - {info['yr']} - {info['sec']}")

# --- 2. AI CONFIG ---
# Is dummy key ki jagah apni Gemini Key paste karna must hai!
API_KEY = "AIzaSyCN6WgtYUCjtMSFcza8zWumohMw-mH399w"

try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    ai_ready = True
except Exception as e:
    ai_ready = False
    st.error(f"AI Key Error: {e}")

# --- 3. HELPER FUNCTIONS ---
def create_archive_path(university, course, year, section, subject):
    today = datetime.now().strftime("%Y-%m-%d")
    path = os.path.join(BASE_DIR, university, course, year, section, subject, today)
    if not os.path.exists(path): os.makedirs(path)
    return path

def generate_notes_4way(content):
    if ai_ready:
        prompt = f"Format into 4 parts: Simple Detailed, Short & Sharp, Bullet Points, and End-Time Revision Notes: {content}"
        res = model.generate_content(prompt)
        return res.text
    return "AI not ready."

# --- 4. SIDEBAR: SECURE LOGIN (Role Keys) ---
st.sidebar.title("🛡️ AKTU ERP Portal")
role = st.sidebar.selectbox("Your Role", ["Select Role", "Authority", "Teacher", "Student", "Parent"])

access_granted = False
if role != "Select Role":
    pwd_input = st.sidebar.text_input(f"Enter {role} Password", type="password")
    if pwd_input == st.session_state.user_db[role]:
        access_granted = True
        st.sidebar.success(f"Verified: {role} ✅")
    elif pwd_input != "":
        st.sidebar.error("Incorrect Role Password ❌")

# --- 5. MAIN INTERFACE ---
if access_granted:
    st.title(f"🎓 AKTU AI Dashboard - {role}")
    
    # Portal Selection
    all_portals = list(st.session_state.aktu_portals.keys())
    selected_sec = st.selectbox("Choose Section Portal", ["--- Select Section ---"] + all_portals)
    
    if selected_sec != "--- Select Section ---":
        # LEVEL 2 KEY (Section Secret Key)
        st.markdown("---")
        st.subheader("🔑 Section Privacy Lock")
        sec_key = st.text_input("Enter Section Secret Key (Default is 123)", type="password")
        
        if sec_key == st.session_state.aktu_portals[selected_sec]["pwd"]:
            p_info = st.session_state.aktu_portals[selected_sec]
            st.success(f"Authorized Class: {p_info['course']} - {p_info['yr']} (Section {p_info['sec']})")
            
            # TABS based on Role
            t1, t2, t3, t4 = st.tabs(["📂 Archive Hub", "🎙️ AI Note Maker", "💬 Class Chat", "🛡️ Admin Audit"])

            # --- TAB 1: ARCHIVE HUB ---
            with t1:
                st.subheader("📚 Subject Repository")
                subj = st.text_input("Subject (e.g., Python, Maths)")
                
                if role == "Teacher" and subj:
                    file = st.file_uploader("Upload Notes/Photo")
                    if file and st.button("Archive subject-wise"):
                        path = create_archive_path(p_info['course'], "BTech", p_info['yr'], p_info['sec'], subj)
                        with open(os.path.join(path, file.name), "wb") as f:
                            f.write(file.getbuffer())
                        st.success("File Archived successfully! 📁")

                if subj:
                    st.write("Browse Subject Data")
                    base_path = os.path.join(BASE_DIR, "BTech", p_info['yr'], p_info['sec'], subj)
                    if os.path.exists(base_path):
                        for dt in os.listdir(base_path):
                            with st.expander(f"📅 Date: {dt}"):
                                for f in os.listdir(os.path.join(base_path, dt)):
                                    st.write(f"📄 {f}")
                                    st.download_button("Download", b"Dummy", file_name=f, key=f+dt+selected_sec)
                    else: st.info("No records yet.")

            # --- TAB 2: AI NOTE MAKER ---
            with t2:
                st.subheader("🤖 AI 4-Step Note Generator")
                raw_text = st.text_area("Paste content:")
                if st.button("Generate Notes"):
                    if ai_ready and raw_text:
                        with st.spinner("AI analyzing..."):
                            st.markdown(generate_notes_4way(raw_text))
                    elif not raw_text: st.warning("Kuch content daalo pehle.")
                    else: st.error("AI not ready.")

            # --- TAB 3: SECURE CHAT ---
            with t3:
                st.subheader(f"💬 Class Chat - {p_info['sec']}")
                if selected_sec not in st.session_state.chats:
                    st.session_state.chats[selected_sec] = []

                for msg in st.session_state.chats[selected_sec]:
                    with st.chat_message(msg["role"]):
                        st.write(f"**{msg['user']}:** {msg['text']} ({msg['time']})")

                chat_in = st.chat_input("Send a message...")
                if chat_in:
                    st.session_state.chats[selected_sec].append({
                        "role": "user" if role == "Student" else "assistant",
                        "user": role, "text": chat_in, "time": datetime.now().strftime("%H:%M")
                    })
                    st.rerun()

            # --- TAB 4: ADMIN AUDIT ---
            with t4:
                st.subheader("🛡️ Feedback & Audit Logs")
                if role in ["Student", "Teacher"]:
                    st.info("Write a review anonymously for Authority.")
                    rev_in = st.text_area("Review/Feedback:")
                    if st.button("Send Anonymous Review"):
                        st.session_state.reviews.append({"from": role, "text": rev_in, "section": selected_sec, "date": datetime.now().strftime("%Y-%m-%d")})
                        st.success("Submitted Secretly. 🛡️")

                if role in ["Authority", "Parent"]:
                    st.warning("Audit Logs - Authority View")
                    for r in st.session_state.reviews:
                        if r["section"] == selected_sec:
                            st.write(f"**[{r['date']}] {r['from']}:** {r['text']}")

        elif sec_key != "": st.error("Wrong Section Key.")

else:
    # PROFESSIONAL WELCOME SCREEN
    st.title("🏛️ Welcome to AKTU AI Smart Campus")
    st.markdown("""
    ### Secure Enterprise Resource Planning (ERP)
    Welcome to the AKTU's secure digital ecosystem. This platform utilizes multi-level authentication and advanced encryption for data isolation.

    **System Guidelines:**
    1.  **Level 1 Key:** Use your Role Password (`student123`, `teacher123`) from the sidebar.
    2.  **Level 2 Key:** Enter your specific Section Secret Key (`123` for dummy data) once logged in.
    3.  **Data Isolation:** Data is strictly isolated by Year and Section.

    Please use the sidebar to authenticate and continue.
    """)
    st.info("Unauthorized access is strictly monitored.")
