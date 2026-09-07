import streamlit as st
import pandas as pd
import re
from datetime import datetime

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Smart Campus - College Admin",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# COLLEGE DIRECTORY
# =========================================================
COLLEGE_DIRECTORY = {
    "KJ Somaiya College": "KJ011",
    "S.M. Shetty College": "SM011",
    "Ramniranjan Jhunjhunwala College": "RJ011"
}
CODE_TO_COLLEGE = {
    code: name for name, code in COLLEGE_DIRECTORY.items()
}

# =========================================================
# STATE -> CITY
# =========================================================
STATE_CITIES = {
    "Andhra Pradesh": ["Visakhapatnam", "Vijayawada", "Guntur", "Nellore", "Kurnool", "Tirupati", "Rajahmundry", "Kadapa"],
    "Arunachal Pradesh": ["Itanagar", "Naharlagun", "Pasighat", "Tawang"],
    "Assam": ["Guwahati", "Dibrugarh", "Silchar", "Jorhat", "Tezpur", "Nagaon"],
    "Bihar": ["Patna", "Gaya", "Bhagalpur", "Muzaffarpur", "Darbhanga", "Purnia"],
    "Chhattisgarh": ["Raipur", "Bhilai", "Bilaspur", "Korba", "Durg", "Rajnandgaon"],
    "Goa": ["Panaji", "Margao", "Vasco da Gama", "Mapusa"],
    "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar", "Jamnagar", "Gandhinagar"],
    "Haryana": ["Gurugram", "Faridabad", "Panipat", "Ambala", "Hisar", "Rohtak", "Karnal"],
    "Himachal Pradesh": ["Shimla", "Manali", "Dharamshala", "Solan", "Mandi", "Kullu"],
    "Jharkhand": ["Ranchi", "Jamshedpur", "Dhanbad", "Bokaro", "Deoghar", "Hazaribagh"],
    "Karnataka": ["Bengaluru", "Mysuru", "Mangaluru", "Hubballi", "Belagavi", "Dharwad", "Shivamogga"],
    "Kerala": ["Thiruvananthapuram", "Kochi", "Kozhikode", "Thrissur", "Kollam", "Kannur", "Alappuzha"],
    "Madhya Pradesh": ["Bhopal", "Indore", "Gwalior", "Jabalpur", "Ujjain", "Sagar"],
    "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Nashik", "Thane", "Navi Mumbai", "Aurangabad", "Kolhapur", "Solapur", "Amravati"],
    "Manipur": ["Imphal", "Thoubal", "Bishnupur", "Churachandpur"],
    "Meghalaya": ["Shillong", "Tura", "Jowai", "Nongpoh"],
    "Mizoram": ["Aizawl", "Lunglei", "Champhai", "Kolasib"],
    "Nagaland": ["Kohima", "Dimapur", "Mokokchung", "Tuensang"],
    "Odisha": ["Bhubaneswar", "Cuttack", "Rourkela", "Puri", "Berhampur", "Sambalpur"],
    "Punjab": ["Amritsar", "Ludhiana", "Jalandhar", "Patiala", "Bathinda", "Mohali"],
    "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur", "Kota", "Ajmer", "Bikaner", "Alwar"],
    "Sikkim": ["Gangtok", "Namchi", "Gyalshing", "Mangan"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem", "Tirunelveli", "Erode"],
    "Telangana": ["Hyderabad", "Warangal", "Nizamabad", "Karimnagar", "Khammam", "Secunderabad"],
    "Tripura": ["Agartala", "Udaipur", "Dharmanagar", "Kailasahar"],
    "Uttar Pradesh": ["Lucknow", "Kanpur", "Agra", "Varanasi", "Prayagraj", "Noida", "Ghaziabad", "Meerut", "Bareilly", "Gorakhpur"],
    "Uttarakhand": ["Dehradun", "Haridwar", "Rishikesh", "Nainital", "Haldwani", "Roorkee"],
    "West Bengal": ["Kolkata", "Howrah", "Durgapur", "Siliguri", "Asansol", "Darjeeling"],
    "Andaman and Nicobar Islands": ["Port Blair", "Diglipur", "Mayabunder"],
    "Chandigarh": ["Chandigarh"],
    "Dadra and Nagar Haveli and Daman and Diu": ["Daman", "Diu", "Silvassa"],
    "Delhi": ["New Delhi", "Delhi"],
    "Jammu and Kashmir": ["Srinagar", "Jammu", "Anantnag", "Baramulla"],
    "Ladakh": ["Leh", "Kargil"],
    "Lakshadweep": ["Kavaratti", "Agatti", "Amini"],
    "Puducherry": ["Puducherry", "Karaikal", "Mahe", "Yanam"]
}

# =========================================================
# SESSION STATE INITIALIZATION
# =========================================================
defaults = {
    "logged_in": False,
    "account_created": False,
    "college_info": {},
    "admin_password": "",
    "verification_status": "Not Submitted",
    "teachers": [],
    "students": [],
    "non_teaching_staff": [],
    "administration_staff": [],
    "security_staff": [],
    "announcements": [],
    "campus_issues": [],
    "clubs": [],
    "student_council": [],
    "timetables": {},
    "dept_data": {},
    "onboarding_step": 1,
    "auth_page": "signup",
    "registration_success": False,
    "admin_menu": "Dashboard",
    "fab_expanded": False,
    "fab_action": None
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# =========================================================
# VALIDATION FUNCTIONS
# =========================================================
def valid_email(email):
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return re.fullmatch(pattern, email.strip()) is not None

def valid_phone(phone):
    phone = phone.strip()
    return phone.isdigit() and len(phone) == 10

def valid_pin(pin):
    pin = pin.strip()
    return pin.isdigit() and len(pin) == 6

# =========================================================
# HELPERS
# =========================================================
def get_departments():
    return [
        "FY BBI",
        "SY BBI",
        "TY BBI",
        "B.Sc Data Science",
        "B.Sc IT",
        "B.Com",
        "BBA",
        "BA"
    ]

def get_subjects():
    return [
        "Mathematics",
        "Python",
        "Data Science",
        "Database Management",
        "Statistics",
        "Machine Learning",
        "Computer Networks",
        "Web Development"
    ]

# =========================================================
# TOP NAVBAR (Logged Out)
# =========================================================
def render_top_nav():
    st.markdown(
        """
        <style>
        .top-navbar {
            padding: 10px 0 14px 0;
            border-bottom: 1px solid #dddddd;
            margin-bottom: 20px;
        }
        .brand-text {
            font-size: 25px;
            font-weight: 700;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    col1, col2, col3 = st.columns([5, 1, 1])
    with col1:
        st.markdown('<div class="brand-text">🏫 Smart Campus</div>', unsafe_allow_html=True)
    with col2:
        if st.button("Sign Up", use_container_width=True):
            st.session_state.auth_page = "signup"
            st.session_state.registration_success = False
            st.rerun()
    with col3:
        if st.button("Sign In", use_container_width=True):
            st.session_state.auth_page = "signin"
            st.rerun()

# =========================================================
# FLOATING ACTION BUTTON (Gmail Style)
# =========================================================
def render_floating_action_button():
    st.markdown("""
        <style>
        .fab-container {
            position: fixed;
            bottom: 30px;
            right: 30px;
            z-index: 9999;
            display: flex;
            flex-direction: column-reverse;
            align-items: flex-end;
            gap: 10px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("---")
        st.subheader("⚡ Quick Actions (+)")
        action = st.selectbox(
            "Select Quick Action",
            [
                "Choose Action...",
                "✏️ Compose Announcement",
                "📤 Upload Timetable",
                "📁 Upload Department Data",
                "🎭 Add Club",
                "🗳️ Add Student Council Notice",
                "🚨 Add Campus Issue",
                "👥 Add Staff"
            ],
            key="quick_action_select"
        )
        if action != "Choose Action...":
            st.session_state.fab_action = action

    if st.session_state.fab_action:
        act = st.session_state.fab_action
        st.session_state.fab_action = None
        if "Announcement" in act:
            st.session_state.admin_menu = "Announcements"
        elif "Timetable" in act:
            st.session_state.admin_menu = "Timetable"
        elif "Department" in act:
            st.session_state.admin_menu = "Departments"
        elif "Club" in act:
            st.session_state.admin_menu = "Clubs"
        elif "Council" in act:
            st.session_state.admin_menu = "Student Council"
        elif "Issue" in act:
            st.session_state.admin_menu = "Campus Issues"
        elif "Staff" in act:
            st.session_state.admin_menu = "Data Entry"
        st.rerun()

# =========================================================
# LOGGED OUT STATE
# =========================================================
if not st.session_state.logged_in:
    render_top_nav()
    
    # SIGN UP PAGE
    if st.session_state.auth_page == "signup":
        st.title("📝 College Registration")
        st.caption("Register your college to access Smart Campus.")
        
        with st.form("college_registration"):
            st.subheader("College Information")
            col1, col2 = st.columns(2)
            with col1:
                college_name = st.selectbox(
                    "College Name *",
                    ["Select College"] + list(COLLEGE_DIRECTORY.keys())
                )
                college_code = st.selectbox(
                    "College Code *",
                    ["Select College Code"] + list(COLLEGE_DIRECTORY.values())
                )
                university = st.text_input("University / Affiliation *")
                principal = st.text_input("Principal *")
                official_email = st.text_input("Official College Email *")
                contact_number = st.text_input("College Contact Number *", max_chars=10)
            
            with col2:
                full_address = st.text_area("Full Address *")
                state = st.selectbox("State *", ["Select State"] + sorted(STATE_CITIES.keys()))
                if state != "Select State":
                    city = st.selectbox("City *", ["Select City"] + STATE_CITIES[state])
                else:
                    city = st.selectbox("City *", ["Select State First"])
                pin_code = st.text_input("PIN Code *", max_chars=6)
                established_year = st.number_input(
                    "Established Year *",
                    min_value=1800,
                    max_value=datetime.now().year,
                    value=2000
                )
            
            st.subheader("College Details")
            col3, col4 = st.columns(2)
            with col3:
                student_capacity = st.number_input("Student Capacity *", min_value=1, value=100)
                college_website = st.text_input("College Website")
            with col4:
                college_logo = st.file_uploader("College Logo / Official Image", type=["png", "jpg", "jpeg"])
            
            st.subheader("Create Admin Account")
            col5, col6 = st.columns(2)
            with col5:
                password = st.text_input("Create Password *", type="password")
            with col6:
                confirm_password = st.text_input("Confirm Password *", type="password")
                
            submit_registration = st.form_submit_button("Create College Account", use_container_width=True)

        if submit_registration:
            errors = []
            if college_name == "Select College":
                errors.append("Please select a college.")
            if college_code == "Select College Code":
                errors.append("Please select a college code.")
            if college_name != "Select College" and college_code != "Select College Code":
                if COLLEGE_DIRECTORY[college_name] != college_code:
                    errors.append("College Name and College Code do not match.")
            if not university.strip():
                errors.append("University / Affiliation is required.")
            if not principal.strip():
                errors.append("Principal name is required.")
            if not valid_email(official_email):
                errors.append("Please enter a valid college email.")
            if not valid_phone(contact_number):
                errors.append("Contact number must contain exactly 10 digits.")
            if not full_address.strip():
                errors.append("Full address is required.")
            if state == "Select State":
                errors.append("Please select a state.")
            if state != "Select State" and city == "Select City":
                errors.append("Please select a city.")
            if not valid_pin(pin_code):
                errors.append("PIN Code must contain exactly 6 digits.")
            if not password:
                errors.append("Password is required.")
            if password != confirm_password:
                errors.append("Passwords do not match.")
                
            if errors:
                for error in errors:
                    st.error(error)
            else:
                st.session_state.college_info = {
                    "College Name": college_name,
                    "College Code": college_code,
                    "University": university,
                    "Principal": principal,
                    "Official Email": official_email,
                    "Contact Number": contact_number,
                    "Address": full_address,
                    "State": state,
                    "City": city,
                    "PIN Code": pin_code,
                    "Established Year": established_year,
                    "Student Capacity": student_capacity,
                    "College Website": college_website,
                    "College Logo": college_logo.name if college_logo else ""
                }
                st.session_state.admin_password = password
                st.session_state.account_created = True
                st.session_state.verification_status = "Not Submitted"
                st.session_state.registration_success = True
                st.session_state.auth_page = "signin"
                st.rerun()

    # SIGN IN PAGE
    elif st.session_state.auth_page == "signin":
        if st.session_state.registration_success:
            st.success("✅ Registration Completed Successfully! Your college has been registered. You can now sign in.")
        st.title("🔐 College Admin Sign In")
        
        if not st.session_state.account_created:
            st.info("Please create your college account first using Sign Up.")
        else:
            with st.form("signin_form"):
                email = st.text_input("Official College Email")
                password = st.text_input("Password", type="password")
                login = st.form_submit_button("Sign In", use_container_width=True)
                
            if login:
                registered_email = st.session_state.college_info.get("Official Email", "")
                if email.strip().lower() == registered_email.strip().lower() and password == st.session_state.admin_password:
                    st.session_state.logged_in = True
                    st.session_state.registration_success = False
                    st.session_state.admin_menu = "Dashboard"
                    st.rerun()
                else:
                    st.error("Invalid email or password.")

# =========================================================
# LOGGED IN STATE
# =========================================================
else:
    college = st.session_state.college_info
    
    # TOP NAVBAR
    st.markdown(
        """
        <style>
        .logged-navbar {
            padding: 8px 0 14px 0;
            border-bottom: 1px solid #dddddd;
            margin-bottom: 15px;
        }
        .logged-brand {
            font-size: 24px;
            font-weight: 700;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    top_col1, top_col2 = st.columns([6, 1])
    with top_col1:
        st.markdown('<div class="logged-brand">🏫 Smart Campus</div>', unsafe_allow_html=True)
    with top_col2:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.auth_page = "signin"
            st.rerun()

    # SIDEBAR NAVIGATION (UPDATED)
    st.sidebar.title("☰ Smart Campus")
    st.sidebar.success(college.get("College Name", "College Admin"))
    st.sidebar.caption(f"Code: {college.get('College Code', '')}")
    st.sidebar.markdown("---")
    
    # Removed Counselling, Notifications, Chatbot
    sidebar_options = [
        "Dashboard",
        "Data Entry",
        "Departments",
        "Timetable",
        "Announcements",
        "Clubs",
        "Student Council",
        "Campus Issues",
        "Analytics",
        "College Settings"
    ]
    
    menu = st.sidebar.radio("Admin Menu", sidebar_options, key="admin_menu")
    st.sidebar.markdown("---")
    st.sidebar.caption(f"Status: {st.session_state.verification_status}")
    
    # Render floating button action helper
    render_floating_action_button()

    # =========================================================
    # PAGE ROUTING
    # =========================================================
    
    # 1. DASHBOARD
    if menu == "Dashboard":
        st.title("🏠 Admin Dashboard")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Teachers Registered", len(st.session_state.teachers))
        col2.metric("Students Registered", len(st.session_state.students))
        col3.metric("Announcements", len(st.session_state.announcements))
        col4.metric("Campus Issues", len(st.session_state.campus_issues))
        
        st.markdown("---")
        st.subheader("College Quick Details")
        st.write(f"**Principal:** {college.get('Principal', 'N/A')}")
        st.write(f"**Email:** {college.get('Official Email', 'N/A')}")
        st.write(f"**City/State:** {college.get('City', '')}, {college.get('State', '')}")

    # 2. DATA ENTRY
    elif menu == "Data Entry":
        st.title("📂 Data Entry Management")
        
        # TOP NAVIGATION TABS (UPDATED)
        tab_teachers, tab_students, tab_review, tab_more = st.tabs([
            "👨‍🏫 Teachers",
            "🎓 Students",
            "📋 Review & Submit",
            "More ▼"
        ])
        
        with tab_teachers:
            st.header("👨‍🏫 Teacher Data Entry")
            with st.form("teacher_form"):
                col1, col2 = st.columns(2)
                with col1:
                    teacher_name = st.text_input("Teacher Name *")
                    employee_id = st.text_input("Employee ID *")
                    teacher_email = st.text_input("Email *")
                    teacher_phone = st.text_input("Phone Number *", max_chars=10)
                    department = st.selectbox("Department *", ["Select Department"] + get_departments())
                with col2:
                    designation = st.text_input("Designation *")
                    subjects = st.multiselect("Subjects *", get_subjects())
                    qualification = st.text_input("Qualification *")
                    experience = st.number_input("Experience (Years) *", min_value=0, max_value=60, value=0)
                
                add_teacher = st.form_submit_button("➕ Add Teacher", use_container_width=True)
                
            if add_teacher:
                if teacher_name and employee_id and valid_email(teacher_email):
                    st.session_state.teachers.append({
                        "Teacher Name": teacher_name.strip(),
                        "Employee ID": employee_id.strip(),
                        "Email": teacher_email.strip(),
                        "Phone": teacher_phone.strip(),
                        "Department": department,
                        "Designation": designation.strip(),
                        "Subjects": ", ".join(subjects),
                        "Qualification": qualification.strip(),
                        "Experience": experience
                    })
                    st.success("Teacher added successfully!")
                    st.rerun()
                else:
                    st.error("Please fill all mandatory fields correctly.")
                    
            if st.session_state.teachers:
                st.subheader(f"Added Teachers ({len(st.session_state.teachers)})")
                st.dataframe(pd.DataFrame(st.session_state.teachers), use_container_width=True)

        with tab_students:
            st.header("🎓 Student Data Entry")
            capacity = college.get("Student Capacity", 0)
            st.info(f"Capacity: {capacity} | Added: {len(st.session_state.students)}")
            
            with st.form("student_form"):
                col1, col2 = st.columns(2)
                with col1:
                    student_name = st.text_input("Student Name *")
                    roll_number = st.text_input("Roll Number *")
                    enrollment_number = st.text_input("Enrollment Number *")
                    student_email = st.text_input("Email *")
                with col2:
                    student_department = st.selectbox("Department *", ["Select Department"] + get_departments())
                    course = st.text_input("Course *")
                    year = st.selectbox("Year *", ["Select Year", "First Year", "Second Year", "Third Year", "Fourth Year"])
                    division = st.text_input("Division *")
                
                add_student = st.form_submit_button("➕ Add Student", use_container_width=True)
                
            if add_student:
                if student_name and roll_number and valid_email(student_email):
                    st.session_state.students.append({
                        "Student Name": student_name.strip(),
                        "Roll Number": roll_number.strip(),
                        "Enrollment Number": enrollment_number.strip(),
                        "Email": student_email.strip(),
                        "Department": student_department,
                        "Course": course.strip(),
                        "Year": year,
                        "Division": division.strip()
                    })
                    st.success("Student added successfully!")
                    st.rerun()
                else:
                    st.error("Please fill all mandatory fields correctly.")

            if st.session_state.students:
                st.subheader(f"Added Students ({len(st.session_state.students)})")
                st.dataframe(pd.DataFrame(st.session_state.students), use_container_width=True)

        with tab_review:
            st.header("📋 Review & Submit Setup")
            st.write(f"**Teachers Count:** {len(st.session_state.teachers)}")
            st.write(f"**Students Count:** {len(st.session_state.students)}")
            st.write(f"**Non-Teaching Staff:** {len(st.session_state.non_teaching_staff)}")
            st.write(f"**Administration Staff:** {len(st.session_state.administration_staff)}")
            st.write(f"**Security Staff:** {len(st.session_state.security_staff)}")
            
            if st.button("🚀 Submit College Setup for Verification", use_container_width=True):
                st.session_state.verification_status = "Approved"
                st.success("Setup submitted and automatically approved!")
                st.rerun()

        with tab_more:
            sub_tab1, sub_tab2, sub_tab3 = st.tabs(["Non-Teaching Staff", "Administration", "Security"])
            
            with sub_tab1:
                st.subheader("Add Non-Teaching Staff")
                with st.form("non_teaching_form"):
                    nt_name = st.text_input("Staff Name")
                    nt_role = st.text_input("Role / Designation")
                    nt_phone = st.text_input("Phone Number")
                    if st.form_submit_button("Add Non-Teaching Staff"):
                        st.session_state.non_teaching_staff.append({"Name": nt_name, "Role": nt_role, "Phone": nt_phone})
                        st.success("Staff added!")
                        st.rerun()
                if st.session_state.non_teaching_staff:
                    st.dataframe(pd.DataFrame(st.session_state.non_teaching_staff))

            with sub_tab2:
                st.subheader("Add Administration Staff")
                with st.form("admin_staff_form"):
                    adm_name = st.text_input("Admin Staff Name")
                    adm_role = st.text_input("Department / Designation")
                    if st.form_submit_button("Add Administration Staff"):
                        st.session_state.administration_staff.append({"Name": adm_name, "Role": adm_role})
                        st.success("Admin staff added!")
                        st.rerun()
                if st.session_state.administration_staff:
                    st.dataframe(pd.DataFrame(st.session_state.administration_staff))

            with sub_tab3:
                st.subheader("Add Security Staff")
                with st.form("security_staff_form"):
                    sec_name = st.text_input("Security Personnel Name")
                    sec_shift = st.selectbox("Shift", ["Day", "Night", "Rotational"])
                    if st.form_submit_button("Add Security Personnel"):
                        st.session_state.security_staff.append({"Name": sec_name, "Shift": sec_shift})
                        st.success("Security staff added!")
                        st.rerun()
                if st.session_state.security_staff:
                    st.dataframe(pd.DataFrame(st.session_state.security_staff))

    # 3. DEPARTMENTS
    elif menu == "Departments":
        st.title("🏢 Department-wise Management")
        
        # Dynamic Top Navigation Tabs for Departments
        dept_tabs = st.tabs(get_departments())
        
        for idx, dept in enumerate(get_departments()):
            with dept_tabs[idx]:
                st.header(f"Department: {dept}")
                st.subheader("Upload / Add Department Specific Data")
                uploaded_file = st.file_uploader(f"Upload Data/Syllabus/Notice for {dept}", type=["pdf", "csv", "xlsx"], key=f"file_{dept}")
                if uploaded_file:
                    st.session_state.dept_data[dept] = uploaded_file.name
                    st.success(f"Uploaded {uploaded_file.name} for {dept}")
                
                if dept in st.session_state.dept_data:
                    st.info(f"📁 Current Active File: {st.session_state.dept_data[dept]}")

    # 4. TIMETABLE
    elif menu == "Timetable":
        st.title("🕒 College Timetable Management")
        st.subheader("Upload New Timetable")
        
        dept_select = st.selectbox("Select Department for Timetable", get_departments())
        timetable_file = st.file_uploader("Upload Timetable File (PDF / CSV / Image)", type=["pdf", "png", "jpg", "csv"])
        
        if st.button("Upload Timetable", use_container_width=True):
            if timetable_file:
                st.session_state.timetables[dept_select] = timetable_file.name
                st.success(f"Timetable for {dept_select} uploaded successfully!")
            else:
                st.error("Please select a file to upload.")

        st.markdown("---")
        st.subheader("Active Timetables")
        if st.session_state.timetables:
            st.json(st.session_state.timetables)
        else:
            st.write("No timetables uploaded yet.")

    # 5. ANNOUNCEMENTS
    elif menu == "Announcements":
        st.title("📢 Compose & Manage Announcements")
        
        with st.form("announcement_form"):
            title = st.text_input("Announcement Title")
            target = st.multiselect("Target Audience", ["All Students", "Teachers", "Staff"] + get_departments())
            content = st.text_area("Announcement Message Content")
            submit = st.form_submit_button("Post Announcement", use_container_width=True)
            
        if submit:
            if title and content:
                st.session_state.announcements.append({
                    "Title": title,
                    "Target": ", ".join(target) if target else "All",
                    "Content": content,
                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                st.success("Announcement published successfully!")
                st.rerun()
            else:
                st.error("Please fill out the title and content.")
                
        if st.session_state.announcements:
            st.subheader("Recent Announcements")
            st.dataframe(pd.DataFrame(st.session_state.announcements), use_container_width=True)

    # 6. CLUBS
    elif menu == "Clubs":
        st.title("🎭 Clubs & Extra-Curricular Activities")
        
        with st.form("club_form"):
            club_name = st.text_input("Club Name")
            mentor = st.text_input("Faculty Mentor / Head")
            desc = st.text_area("Club Description & Objectives")
            submit_club = st.form_submit_button("Create / Upload Club Details", use_container_width=True)
            
        if submit_club:
            if club_name:
                st.session_state.clubs.append({
                    "Club Name": club_name,
                    "Mentor": mentor,
                    "Description": desc
                })
                st.success("Club registered successfully!")
                st.rerun()

        if st.session_state.clubs:
            st.subheader("Active College Clubs")
            st.dataframe(pd.DataFrame(st.session_state.clubs), use_container_width=True)

    # 7. STUDENT COUNCIL
    elif menu == "Student Council":
        st.title("🗳️ Student Council Management")
        
        with st.form("council_form"):
            member_name = st.text_input("Student Name")
            position = st.selectbox("Council Position", ["General Secretary", "Joint Secretary", "Cultural Head", "Sports Head", "Class Representative"])
            dept = st.selectbox("Department", get_departments())
            submit_council = st.form_submit_button("Create / Upload Council Member", use_container_width=True)
            
        if submit_council:
            if member_name:
                st.session_state.student_council.append({
                    "Name": member_name,
                    "Position": position,
                    "Department": dept
                })
                st.success("Council member added!")
                st.rerun()

        if st.session_state.student_council:
            st.subheader("Current Student Council Members")
            st.dataframe(pd.DataFrame(st.session_state.student_council), use_container_width=True)

    # 8. CAMPUS ISSUES
    elif menu == "Campus Issues":
        st.title("🚨 Campus Issues & Support Tickets")
        
        with st.form("issue_form"):
            issue_title = st.text_input("Issue Title / Subject")
            category = st.selectbox("Category", ["Infrastructure", "IT Support", "Cleanliness", "Security", "Other"])
            description = st.text_area("Detailed Description")
            submit_issue = st.form_submit_button("Add / Report Campus Issue", use_container_width=True)
            
        if submit_issue:
            if issue_title:
                st.session_state.campus_issues.append({
                    "Title": issue_title,
                    "Category": category,
                    "Description": description,
                    "Status": "Open",
                    "Date": datetime.now().strftime("%Y-%m-%d")
                })
                st.success("Campus issue reported successfully!")
                st.rerun()

        if st.session_state.campus_issues:
            st.subheader("Reported Issues")
            st.dataframe(pd.DataFrame(st.session_state.campus_issues), use_container_width=True)

    # 9. ANALYTICS
    elif menu == "Analytics":
        st.title("📈 Campus Analytics & Overview")
        st.caption("Viewing and Analysis Focused Platform")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Student Distribution")
            if st.session_state.students:
                df_stud = pd.DataFrame(st.session_state.students)
                st.bar_chart(df_stud['Department'].value_counts())
            else:
                st.info("No student data available for charts.")
                
        with col2:
            st.subheader("Teacher Distribution")
            if st.session_state.teachers:
                df_teach = pd.DataFrame(st.session_state.teachers)
                st.bar_chart(df_teach['Department'].value_counts())
            else:
                st.info("No teacher data available for charts.")

    # 10. COLLEGE SETTINGS
    elif menu == "College Settings":
        st.title("⚙️ College Settings & Details")
        st.json(st.session_state.college_info)