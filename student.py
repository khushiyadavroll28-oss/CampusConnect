import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from collections import deque

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(page_title="Student Portal", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================
if 'users_db' not in st.session_state:
    st.session_state.users_db = {}

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'current_user' not in st.session_state:
    st.session_state.current_user = None

if 'current_page' not in st.session_state:
    st.session_state.current_page = "Dashboard"

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "Hello! I am your Academic Assistant 🤖. How can I help you today?"}
    ]

def do_rerun():
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()

# ==========================================
# CUSTOM STYLING (CSS)
# ==========================================
st.markdown("""
<style>
    .stApp {
        background-color: #f7f9fc;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .events-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 12px 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .events-title {
        font-size: 16px;
        font-weight: bold;
    }
    
    .card-box {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border: 1px solid #eef2f5;
    }
    .card-title {
        color: #1e3c72;
        font-size: 18px;
        font-weight: 700;
        margin-bottom: 15px;
    }
    .step-box {
        background: #f8fafc;
        border-left: 4px solid #1e3c72;
        padding: 10px 15px;
        margin-bottom: 8px;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# AUTHENTICATION MODULE
# ==========================================
def render_auth_page():
    st.markdown("<h2 style='text-align: center; color: #1e3c72;'>🎓 Student Portal Authentication</h2>", unsafe_allow_html=True)
    st.write("")
    
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        tab_signup, tab_login, tab_demo = st.tabs(["📝 Student Registration", "🔑 Sign In", "⚡ Quick Demo Login"])
        
        with tab_signup:
            st.subheader("Student & College Registration")
            with st.form("registration_form"):
                st.markdown("##### 👤 Personal Details")
                c1, c2 = st.columns(2)
                with c1:
                    full_name = st.text_input("Full Name", placeholder="e.g. Niti Kashyap")
                    roll_no = st.text_input("Roll Number / Student ID", placeholder="e.g. BSC-DS-042")
                with c2:
                    student_email = st.text_input("Email Address", placeholder="student@college.edu")
                    address = st.text_input("Residential Address", placeholder="Powai, Mumbai")
                    
                st.markdown("##### 🏫 College & Academic Details")
                c3, c4 = st.columns(2)
                with c3:
                    college_name = st.text_input("College / Institute Name", value="SM Shetty College")
                    college_code = st.text_input("College Code", value="SMS-2026")
                with c4:
                    branch = st.selectbox("Branch / Course", ["B.Sc Data Science", "B.Tech Computer Science", "B.Sc IT", "B.CA", "Other"])
                    year_sem = st.selectbox("Year / Semester", ["1st Year (Sem 1)", "1st Year (Sem 2)", "2nd Year (Sem 3)", "2nd Year (Sem 4)", "3rd Year (Sem 5)", "3rd Year (Sem 6)"])
                    
                st.markdown("##### 🔒 Security")
                c5, c6 = st.columns(2)
                with c5:
                    reg_pass = st.text_input("Choose Password", type="password")
                with c6:
                    confirm_pass = st.text_input("Confirm Password", type="password")
                
                submit_reg = st.form_submit_button("Complete Registration & Enter Portal", use_container_width=True)
                
                if submit_reg:
                    email_clean = student_email.strip().lower()
                    name_clean = full_name.strip()
                    roll_clean = roll_no.strip()
                    
                    if not name_clean or not roll_clean or not email_clean or not reg_pass:
                        st.error("Please fill in Full Name, Roll No, Email, and Password.")
                    elif reg_pass != confirm_pass:
                        st.error("Passwords do not match!")
                    else:
                        st.session_state.users_db[email_clean] = {
                            "password": reg_pass,
                            "full_name": name_clean,
                            "roll_no": roll_clean,
                            "branch": branch,
                            "year_sem": year_sem,
                            "college_name": college_name.strip() if college_name else "SM Shetty College",
                            "college_code": college_code.strip() if college_code else "SMS-2026",
                            "address": address.strip() if address else "Powai, Mumbai"
                        }
                        st.session_state.authenticated = True
                        st.session_state.current_user = email_clean
                        st.success("✅ Account created successfully! Logging you in...")
                        do_rerun()

        with tab_login:
            st.subheader("Sign In")
            with st.form("login_form"):
                login_email = st.text_input("Student Email Address")
                login_pass = st.text_input("Password", type="password")
                submit_login = st.form_submit_button("Sign In", use_container_width=True)
                
                if submit_login:
                    login_email_clean = login_email.strip().lower()
                    if not login_email_clean or not login_pass:
                        st.error("Please enter both credentials.")
                    elif login_email_clean not in st.session_state.users_db:
                        st.error("Account does not exist in active session. Please register or use Quick Demo Login.")
                    elif st.session_state.users_db[login_email_clean]["password"] != login_pass:
                        st.error("Incorrect password! Please try again.")
                    else:
                        st.session_state.authenticated = True
                        st.session_state.current_user = login_email_clean
                        st.success("Successfully signed in!")
                        do_rerun()

        with tab_demo:
            st.subheader("Bypass Sign In (Instant Access)")
            if st.button("🚀 One-Click Login as Student", use_container_width=True):
                demo_email = "student@smshetty.edu"
                st.session_state.users_db[demo_email] = {
                    "password": "123",
                    "full_name": "Niti Kashyap",
                    "roll_no": "BSC-DS-042",
                    "branch": "B.Sc Data Science",
                    "year_sem": "2nd Year (Sem 3)",
                    "college_name": "SM Shetty College",
                    "college_code": "SMS-2026",
                    "address": "Powai, Mumbai"
                }
                st.session_state.authenticated = True
                st.session_state.current_user = demo_email
                do_rerun()

# ==========================================
# CAMPUS GRAPH & NAVIGATION DATA
# ==========================================
MAIN_BLOCK_COORDS = (19.0728, 72.8826)
COURTYARD_COORDS = (19.0732, 72.8831)
LIBRARY_BLOCK_COORDS = (19.0736, 72.8836)

NODE_INFO = {
    "Main Entrance": {"floor": "Ground Floor", "building": "Main Block", "coords": MAIN_BLOCK_COORDS},
    "Reception": {"floor": "Ground Floor", "building": "Main Block", "coords": MAIN_BLOCK_COORDS},
    "Canteen": {"floor": "Ground Floor", "building": "Main Block", "coords": MAIN_BLOCK_COORDS},
    "Admin Office": {"floor": "Ground Floor", "building": "Main Block", "coords": MAIN_BLOCK_COORDS},
    "Staircase - Main Block": {"floor": "Ground Floor", "building": "Main Block", "coords": MAIN_BLOCK_COORDS},
    "Classroom 101": {"floor": "First Floor", "building": "Main Block", "coords": MAIN_BLOCK_COORDS},
    "Computer Lab": {"floor": "First Floor", "building": "Main Block", "coords": MAIN_BLOCK_COORDS},
    "Courtyard Pathway": {"floor": "Outdoors", "building": "Courtyard", "coords": COURTYARD_COORDS},
    "Library Entrance": {"floor": "Ground Floor", "building": "Library Block", "coords": LIBRARY_BLOCK_COORDS},
    "Library": {"floor": "First Floor", "building": "Library Block", "coords": LIBRARY_BLOCK_COORDS},
}

EDGES = [
    ("Main Entrance", "Reception"), ("Reception", "Canteen"), ("Reception", "Admin Office"),
    ("Reception", "Staircase - Main Block"), ("Staircase - Main Block", "Classroom 101"), 
    ("Classroom 101", "Computer Lab"), ("Main Entrance", "Courtyard Pathway"), 
    ("Courtyard Pathway", "Library Entrance"), ("Library Entrance", "Library")
]

CAMPUS_GRAPH = {node: [] for node in NODE_INFO}
for a, b in EDGES:
    CAMPUS_GRAPH[a].append(b)
    CAMPUS_GRAPH[b].append(a)

def bfs_shortest_path(graph, start, goal):
    if start == goal:
        return [start]
    visited = {start}
    queue = deque([[start]])
    while queue:
        path = queue.popleft()
        node = path[-1]
        for neighbor in graph.get(node, []):
            if neighbor == goal:
                return path + [neighbor]
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(path + [neighbor])
    return None

def generate_detailed_directions(path):
    directions = []
    directions.append(f"🏁 **Start Journey** from **{path[0]}** ({NODE_INFO[path[0]]['building']}, {NODE_INFO[path[0]]['floor']}).")
    for i in range(len(path) - 1):
        curr, nxt = path[i], path[i+1]
        curr_b, nxt_b = NODE_INFO[curr]['building'], NODE_INFO[nxt]['building']
        curr_f, nxt_f = NODE_INFO[nxt]['floor'], NODE_INFO[nxt]['floor']
        if curr_b != nxt_b:
            directions.append(f"🚪 Exit **{curr_b}** and walk through **{nxt_b}** toward **{nxt}**.")
        elif curr_f != nxt_f:
            directions.append(f"🪜 Take stairs/elevator from **{curr_f}** to **{nxt_f}** to reach **{nxt}**.")
        else:
            directions.append(f"🚶 Walk straight down the corridor from **{curr}** to **{nxt}**.")
    directions.append(f"🎯 **Destination Reached:** You have arrived at **{path[-1]}**!")
    return directions

# ==========================================
# MAIN APPLICATION
# ==========================================
if not st.session_state.authenticated:
    render_auth_page()
else:
    user_info = st.session_state.users_db.get(st.session_state.current_user, {})
    
    st.markdown(f"""
    <div class="events-header">
        <div>
            <span class="events-title">📢 IMPORTANT NOTICE:</span> 
            <span>Mid-Semester Examination Schedule has been uploaded. Check the Syllabus section.</span>
        </div>
        <div>🏫 <b>{user_info.get('college_name', 'College Portal')}</b> ({user_info.get('college_code', 'Code')})</div>
    </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.title("📌 Student Profile")
        st.write(f"👤 **{user_info.get('full_name', 'Student')}**")
        st.caption(f"🆔 Roll No: {user_info.get('roll_no', 'N/A')}")
        st.caption(f"🎓 Course: {user_info.get('branch', 'N/A')}")
        st.caption(f"📅 Year: {user_info.get('year_sem', 'N/A')}")
        st.caption(f"🏠 Address: {user_info.get('address', 'N/A')}")
        st.divider()
        
        pages = ["Dashboard", "Timetable", "Attendance", "Assignments", "Syllabus", "Events", "Report Issue", "Campus Navigator", "AI Chatbot"]
        selected_page = st.radio("Navigate to:", pages, index=pages.index(st.session_state.current_page))
        st.session_state.current_page = selected_page
        
        st.divider()
        if st.button("🚪 Sign Out", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.current_user = None
            st.session_state.current_page = "Dashboard"
            do_rerun()

    current = st.session_state.current_page

    # ==========================================
    # DASHBOARD PAGE WITH ALL PLOTLY CHARTS
    # ==========================================
    if current == "Dashboard":
        st.markdown(f"<h2 style='color:#1e3c72;'>📊 Academic Dashboard - {user_info.get('full_name')}</h2>", unsafe_allow_html=True)
        
        # Metrics Row
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Overall Attendance", "86.5%", delta="1.5%")
        with m2:
            st.metric("Total Conducted", "60 Lectures")
        with m3:
            st.metric("Lectures Attended", "52 Sessions")
        with m4:
            st.metric("Status", "Eligible", delta_color="normal")

        st.markdown("<br>", unsafe_allow_html=True)

        # Charts Row 1: Gauge Chart & Subject Attendance Bar Chart
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown('<div class="card-box">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">🎯 Attendance Gauge</div>', unsafe_allow_html=True)
            
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=86.5,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Overall %"},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "#1e3c72"},
                    'steps': [
                        {'range': [0, 75], 'color': "#ffcdd2"},
                        {'range': [75, 100], 'color': "#c8e6c9"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 75
                    }
                }
            ))
            fig_gauge.update_layout(height=280, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_gauge, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="card-box">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">📊 Subject-wise Attendance Breakdown</div>', unsafe_allow_html=True)
            
            subjects_df = pd.DataFrame({
                'Subject': ['Data Structures', 'DBMS', 'Operating Systems', 'Mathematics', 'Computer Networks'],
                'Attended': [18, 16, 17, 15, 14],
                'Total': [20, 20, 20, 18, 18],
                'Percentage': [90.0, 80.0, 85.0, 83.3, 77.8]
            })

            fig_bar = px.bar(
                subjects_df, 
                x='Subject', 
                y='Percentage', 
                text='Percentage',
                color='Percentage',
                color_continuous_scale=['#e53935', '#fdd835', '#43a047'],
                range_y=[0, 100]
            )
            fig_bar.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig_bar.add_hline(y=75, line_dash="dash", line_color="red", annotation_text="Min 75% Required")
            fig_bar.update_layout(height=280, margin=dict(l=20, r=20, t=30, b=20), coloraxis_showscale=False)
            st.plotly_chart(fig_bar, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Charts Row 2: Attendance Monthly Trend Line Chart
        st.markdown('<div class="card-box">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📈 Monthly Attendance Trend</div>', unsafe_allow_html=True)
        
        trend_df = pd.DataFrame({
            'Month': ['July', 'August', 'September', 'October', 'November'],
            'Attendance %': [92.0, 88.5, 84.0, 86.5, 89.0]
        })

        fig_line = px.line(
            trend_df, 
            x='Month', 
            y='Attendance %', 
            markers=True, 
            text='Attendance %',
            title=""
        )
        fig_line.update_traces(line_color='#1e3c72', line_width=3, marker_size=8, textposition='top center')
        fig_line.update_layout(height=250, margin=dict(l=20, r=20, t=20, b=20), yaxis_range=[60, 100])
        st.plotly_chart(fig_line, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- CAMPUS NAVIGATOR PAGE ---
    elif current == "Campus Navigator":
        st.markdown('<div class="card-box"><div class="card-title">🗺️ Campus Navigator & Turn-by-Turn Directions</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            start_loc = st.selectbox("I am currently at:", list(NODE_INFO.keys()), index=0)
        with col2:
            end_loc = st.selectbox("I want to go to:", list(NODE_INFO.keys()), index=5)
        
        if st.button("🔍 Get Full Directions", use_container_width=True):
            if start_loc == end_loc:
                st.info("You are already at your destination!")
            else:
                path = bfs_shortest_path(CAMPUS_GRAPH, start_loc, end_loc)
                if path:
                    st.success("Shortest route calculated successfully!")
                    st.markdown("#### 🗺️ Route Summary:")
                    st.code(" ➔ ".join(path))
                    st.markdown("#### 🚶 Turn-by-Turn Directions:")
                    step_by_step = generate_detailed_directions(path)
                    for step in step_by_step:
                        st.markdown(f"<div class='step-box'>{step}</div>", unsafe_allow_html=True)
                else:
                    st.error("No valid path found between selected locations.")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- TIMETABLE PAGE ---
    elif current == "Timetable":
        st.markdown('<div class="card-box"><div class="card-title">📅 Class Timetable</div>', unsafe_allow_html=True)
        timetable_data = {
            "Time Slot": ["09:00 AM - 10:00 AM", "10:15 AM - 11:15 AM", "11:30 AM - 12:30 PM", "02:00 PM - 03:30 PM"],
            "Monday": ["Mathematics", "Physics", "Computer Networks", "Lab Session"],
            "Tuesday": ["DBMS", "Mathematics", "English", "Library"],
            "Wednesday": ["Operating Systems", "Physics", "DBMS Lab", "Free Slot"]
        }
        st.dataframe(pd.DataFrame(timetable_data), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- ATTENDANCE PAGE ---
    elif current == "Attendance":
        st.markdown('<div class="card-box"><div class="card-title">📈 Detailed Subject-Wise Attendance</div>', unsafe_allow_html=True)
        st.write("**Data Structures:** 90% (18/20)")
        st.progress(0.90)
        st.write("**Database Management:** 80% (16/20)")
        st.progress(0.80)
        st.write("**Operating Systems:** 85% (17/20)")
        st.progress(0.85)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- ASSIGNMENTS PAGE ---
    elif current == "Assignments":
        st.markdown('<div class="card-box"><div class="card-title">📝 Homework & Assignments</div>', unsafe_allow_html=True)
        st.warning("📌 **DSA Assignment 3:** Trees & Graphs — Due: Tomorrow, 11:59 PM")
        st.file_uploader("Upload Solution File (PDF/ZIP)", type=["pdf", "zip"])
        st.markdown('</div>', unsafe_allow_html=True)

    # --- SYLLABUS PAGE ---
    elif current == "Syllabus":
        st.markdown('<div class="card-box"><div class="card-title">📖 Subject Syllabus</div>', unsafe_allow_html=True)
        with st.expander("Data Structures & Algorithms"):
            st.markdown("- Unit 1: Arrays & Stacks\n- Unit 2: Trees & DP")
        with st.expander("Database Management Systems"):
            st.markdown("- Unit 1: ER Model\n- Unit 2: SQL")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- EVENTS PAGE ---
    elif current == "Events":
        st.markdown('<div class="card-box"><div class="card-title">🎉 Campus Events</div>', unsafe_allow_html=True)
        st.info("📢 **College Tech Fest 2026** — Registration starts next week!")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- REPORT ISSUE PAGE ---
    elif current == "Report Issue":
        st.markdown('<div class="card-box"><div class="card-title">🚨 Report an Issue</div>', unsafe_allow_html=True)
        with st.form("report_form"):
            category = st.selectbox("Category", ["Harassment", "Infrastructure", "Faculty Complaint", "Other"])
            description = st.text_area("Describe the problem")
            submitted = st.form_submit_button("Submit")
            if submitted:
                st.success("Your report has been successfully submitted.")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- AI CHATBOT PAGE ---
    elif current == "AI Chatbot":
        st.markdown('<div class="card-box"><div class="card-title">🤖 Academic Assistant</div>', unsafe_allow_html=True)
        st.caption("Ask anything about your coursework or portal navigation.")

        for chat in st.session_state.chat_history:
            with st.chat_message(chat["role"]):
                st.markdown(chat["content"])

        user_input = st.chat_input("Ask a question...")
        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            with st.chat_message("assistant"):
                reply = f"I am here to help you with your studies for {user_info.get('branch', 'Data Science')}! (AI Chatbot Mode)"
                st.markdown(reply)
                st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.markdown('</div>', unsafe_allow_html=True)