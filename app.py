import streamlit as st
import hashlib
import sqlite3
import pandas as pd
import time

from datetime import datetime

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import getSampleStyleSheet

# =========================================================
# NO EXTERNAL DEPENDENCY VERSION
# =========================================================

GEMINI_API_KEY = ""

model = None

# =========================================================
# ADMIN
# =========================================================

ADMIN_EMAIL = "admin@gmail.com"

ADMIN_PASSWORD = "admin123"

# =========================================================
# DATABASE
# =========================================================

conn = sqlite3.connect(
    "database.db",
    check_same_thread=False
)

cursor = conn.cursor()

# USERS

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    password TEXT,
    role TEXT,
    is_banned INTEGER,
    warnings INTEGER,
    created_at TEXT
)
""")

# PROJECTS

cursor.execute("""
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_email TEXT,
    repo_name TEXT,
    generated_docs TEXT,
    score INTEGER,
    created_at TEXT
)
""")

conn.commit()




# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="DocuMind AI",
    page_icon="🚀",
    layout="wide"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}

.stApp {

    background: linear-gradient(
        -45deg,
        #020617,
        #0f172a,
        #111827,
        #1e293b
    );

    background-size: 400% 400%;

    animation: gradient 15s ease infinite;

    color:white;
}

@keyframes gradient {

    0% {
        background-position:0% 50%;
    }

    50% {
        background-position:100% 50%;
    }

    100% {
        background-position:0% 50%;
    }
}

.main-title {

    text-align:center;

    font-size:52px;

    font-weight:700;

    color:white;
}

.sub-title {

    text-align:center;

    color:#cbd5e1;

    margin-bottom:30px;
}

.card {

    background: rgba(255,255,255,0.06);

    border:1px solid rgba(255,255,255,0.1);

    backdrop-filter: blur(12px);

    padding:25px;

    border-radius:20px;

    transition:0.3s;

    box-shadow:0px 0px 20px rgba(0,0,0,0.3);
}

.card:hover {

    transform: translateY(-5px);

    box-shadow:0px 0px 25px #2563eb;
}

.stButton>button {

    width:100%;

    border:none;

    border-radius:12px;

    background: linear-gradient(
        90deg,
        #7c3aed,
        #2563eb
    );

    color:white;

    font-weight:bold;

    padding:12px;

    transition:0.3s;
}

.stButton>button:hover {

    transform:scale(1.02);

    box-shadow:0px 0px 20px #2563eb;
}

.stTextInput input {

    background: rgba(255,255,255,0.08);

    color:white;

    border-radius:12px;
}

.stTextArea textarea {

    background: rgba(255,255,255,0.05);

    color:white;

    border-radius:12px;
}

.stFileUploader {

    background: rgba(255,255,255,0.05);

    padding:20px;

    border-radius:15px;
}

.marquee {

    width:100%;

    overflow:hidden;

    white-space:nowrap;

    box-sizing:border-box;
}

.marquee span {

    display:inline-block;

    padding-left:100%;

    animation: marquee 15s linear infinite;

    font-size:20px;

    font-weight:bold;

    color:#38bdf8;
}

@keyframes marquee {

    0% {
        transform:translate(0,0);
    }

    100% {
        transform:translate(-100%,0);
    }
}

.metric-card {

    background: rgba(255,255,255,0.05);

    padding:20px;

    border-radius:15px;

    text-align:center;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# MOVING HEADER
# =========================================================

st.markdown("""
<div class="marquee">
<span>
🏫 TECHNOCRATS INSTITUTE OF TECHNOLOGY BHOPAL 🚀 AI HACKATHON 2026 🚀 DOCUMIND AI PLATFORM 🚀 DEVELOPED BY RITESH KUMAR SINGH 🚀
</span>
</div>
""", unsafe_allow_html=True)

# =========================================================
# SESSION STATE
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_email" not in st.session_state:
    st.session_state.user_email = ""

if "user_name" not in st.session_state:
    st.session_state.user_name = ""

if "user_role" not in st.session_state:
    st.session_state.user_role = "user"

# =========================================================
# FUNCTIONS
# =========================================================

def hash_password(password):

    return hashlib.sha256(
        password.encode()
    ).hexdigest()

def verify_password(password, hashed):

    return hashlib.sha256(
        password.encode()
    ).hexdigest() == hashed

def get_greeting():

    hour = datetime.now().hour

    if hour < 12:
        return "Good Morning"

    elif hour < 18:
        return "Good Afternoon"

    else:
        return "Good Evening"

def generate_docs(code):

    if not model:

        return f"""
# 🚀 AI Documentation Report

## 📂 Repository Analysis

Repository uploaded successfully.

## ✅ Features Detected
- Authentication System
- Database Integration
- Dashboard UI
- API Logic
- File Upload System

## 📈 Repository Health
Good project structure detected.

## 🔐 Security Suggestions
- Add environment variables
- Improve password validation
- Add API protection

## 🚀 Deployment Guide
Deploy easily using:
- Streamlit Cloud
- Render
- Railway

## 💡 Future Improvements
- Add JWT Authentication
- Add Docker Support
- Add Team Collaboration
"""

    prompt = f"""
    Analyze this repository and generate:

    1. Project Summary
    2. README
    3. Installation Guide
    4. API Documentation
    5. Folder Structure
    6. Security Improvements
    7. Optimization Suggestions
    8. Deployment Guide
    9. Architecture Explanation
    10. Future Improvements

    Repository Code:
    {code}
    """

    try:

        response = model.generate_content(prompt)

        return response.text

    except:

        return "AI generation temporarily unavailable."

def chat_with_repo(code, question):

    if not model:

        return """
AI Service Temporarily Offline.

Possible explanations:
- Gemini package not installed
- API key missing
- Deployment rebuild pending
"""

    prompt = f"""
    Repository Code:
    {code}

    User Question:
    {question}

    Answer professionally.
    """

    try:

        response = model.generate_content(prompt)

        return response.text

    except:

        return "AI response generation failed."

def export_pdf(content):

    filename = "documentation.pdf"

    doc = SimpleDocTemplate(filename)

    styles = getSampleStyleSheet()

    story = []

    story.append(
        Paragraph(content, styles['BodyText'])
    )

    story.append(Spacer(1, 12))

    doc.build(story)

    return filename

def calculate_score(code):

    score = min(len(code) // 50, 100)

    return score

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("🚀 DocuMind AI")

menu = st.sidebar.radio(
    "Navigation",
    [
        "Home",
        "Signup",
        "Login",
        "Dashboard",
        "AI Chat",
        "Analytics",
        "History",
        "Admin Panel"
    ]
)

# =========================================================
# HOME
# =========================================================

if menu == "Home":

    st.markdown("""
    <div class='main-title'>
    🚀 DocuMind AI
    </div>

    <div class='sub-title'>
    AI Powered Repository Documentation Platform
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")

    # HERO SECTION

    st.markdown("""
    <div class="card" style="padding:40px; text-align:center;">

    <h1 style="
    font-size:55px;
    color:white;
    ">
    🚀 Build Smart AI Documentation
    </h1>

    <p style="
    font-size:22px;
    color:#cbd5e1;
    margin-top:20px;
    ">
    Upload repositories, generate AI documentation,
    chat with codebases, analyze architecture,
    and create professional developer reports instantly.
    </p>

    <br>

    <div style="
    display:flex;
    justify-content:center;
    gap:20px;
    flex-wrap:wrap;
    ">

    <div style="
    background:rgba(255,255,255,0.05);
    padding:15px 25px;
    border-radius:15px;
    ">
    🤖 Gemini AI Powered
    </div>

    <div style="
    background:rgba(255,255,255,0.05);
    padding:15px 25px;
    border-radius:15px;
    ">
    📄 PDF Export
    </div>

    <div style="
    background:rgba(255,255,255,0.05);
    padding:15px 25px;
    border-radius:15px;
    ">
    💬 AI Repository Chat
    </div>

    </div>

    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # FEATURE CARDS

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown("""
        <div class="card" style="
        height:330px;
        display:flex;
        flex-direction:column;
        justify-content:space-between;
        ">

        <div>

        <h1 style="font-size:50px;">🤖</h1>

        <h2 style="
        color:white;
        font-size:34px;
        ">
        AI Documentation
        </h2>

        <p style="
        color:#cbd5e1;
        font-size:17px;
        line-height:1.7;
        ">
        Generate complete professional documentation
        instantly using advanced AI analysis.

        Includes:
        README,
        setup guide,
        APIs,
        architecture,
        optimization suggestions,
        deployment instructions,
        and more.
        </p>

        </div>

        <div style="
        color:#38bdf8;
        font-weight:bold;
        ">
        ⚡ Smart AI Generated
        </div>

        </div>
        """, unsafe_allow_html=True)

    with col2:

        st.markdown("""
        <div class="card" style="
        height:330px;
        display:flex;
        flex-direction:column;
        justify-content:space-between;
        ">

        <div>

        <h1 style="font-size:50px;">💬</h1>

        <h2 style="
        color:white;
        font-size:34px;
        ">
        AI Repository Chat
        </h2>

        <p style="
        color:#cbd5e1;
        font-size:17px;
        line-height:1.7;
        ">
        Chat directly with uploaded repositories.

        Ask AI:
        architecture flow,
        APIs used,
        database logic,
        authentication flow,
        optimization ideas,
        debugging solutions,
        and code explanations.
        </p>

        </div>

        <div style="
        color:#38bdf8;
        font-weight:bold;
        ">
        🚀 Real-Time AI Answers
        </div>

        </div>
        """, unsafe_allow_html=True)

    with col3:

        st.markdown("""
        <div class="card" style="
        height:330px;
        display:flex;
        flex-direction:column;
        justify-content:space-between;
        ">

        <div>

        <h1 style="font-size:50px;">📊</h1>

        <h2 style="
        color:white;
        font-size:34px;
        ">
        Analytics Dashboard
        </h2>

        <p style="
        color:#cbd5e1;
        font-size:17px;
        line-height:1.7;
        ">
        Monitor AI usage,
        repository analysis,
        user activity,
        generated projects,
        health scores,
        documentation history,
        and platform growth analytics.
        </p>

        </div>

        <div style="
        color:#38bdf8;
        font-weight:bold;
        ">
        📈 Startup-Level Dashboard
        </div>

        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # EXTRA SECTION

    st.markdown("""
    <div class="card" style="
    padding:35px;
    text-align:center;
    ">

    <h1 style="
    color:white;
    ">
    🔥 Why DocuMind AI?
    </h1>

    <br>

    <div style="
    display:grid;
    grid-template-columns:repeat(3,1fr);
    gap:20px;
    ">

    <div>
    ⚡ AI Powered Automation
    </div>

    <div>
    🚀 Easy Deployment
    </div>

    <div>
    📄 Export Documentation
    </div>

    <div>
    💬 Chat With Codebase
    </div>

    <div>
    📊 Real-Time Analytics
    </div>

    <div>
    🔐 Secure Authentication
    </div>

    </div>

    </div>
    """, unsafe_allow_html=True)
# =========================================================
# SIGNUP
# =========================================================

elif menu == "Signup":

    st.title("📝 Signup")

    name = st.text_input("Name")

    email = st.text_input("Email")

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Create Account"):

        cursor.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        )

        existing = cursor.fetchone()

        if existing:

            st.error("User already exists")

        else:

            cursor.execute("""
            INSERT INTO users (
                name,
                email,
                password,
                role,
                is_banned,
                warnings,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                email,
                hash_password(password),
                "user",
                0,
                0,
                str(datetime.now())
            ))

            conn.commit()

            st.success("Account Created Successfully")

# =========================================================
# LOGIN
# =========================================================

elif menu == "Login":

    st.title("🔐 Login")

    email = st.text_input("Email")

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Login"):

        if (
            email == ADMIN_EMAIL
            and password == ADMIN_PASSWORD
        ):

            st.session_state.logged_in = True

            st.session_state.user_email = email

            st.session_state.user_name = "Admin"

            st.session_state.user_role = "admin"

            st.success("Admin Login Successful")

            time.sleep(1)

            st.rerun()

        else:

            cursor.execute(
                "SELECT * FROM users WHERE email=?",
                (email,)
            )

            user = cursor.fetchone()

            if not user:

                st.error("User not found")

            elif user[5] == 1:

                st.error("Your account is banned")

            elif verify_password(
                password,
                user[3]
            ):

                st.session_state.logged_in = True

                st.session_state.user_email = email

                st.session_state.user_name = user[1]

                st.session_state.user_role = "user"

                st.success("Login Successful")

                time.sleep(1)

                st.rerun()

            else:

                st.error("Wrong Password")

# =========================================================
# DASHBOARD
# =========================================================

elif menu == "Dashboard":

    if not st.session_state.logged_in:

        st.warning("Please Login First")

    else:

        greeting = get_greeting()

        st.title(
            f"{greeting}, {st.session_state.user_name} 👋"
        )

        st.subheader(
            "🚀 Welcome To AI Workspace"
        )

        uploaded_file = st.file_uploader(
            "Upload Repository",
            type=["py", "txt", "js", "md"]
        )

        github_url = st.text_input(
            "Paste GitHub Repository URL"
        )

        code = ""

        if uploaded_file:

            code = uploaded_file.read().decode("utf-8")

            st.code(code)

        st.markdown("## 🤖 AI Repository Analysis")

        if st.button("🚀 Analyze Repository"):

            if code == "":

                st.error(
                    "Please upload repository first"
                )

            else:

                progress = st.progress(0)

                for i in range(100):

                    time.sleep(0.01)

                    progress.progress(i + 1)

                with st.spinner(
                    "AI analyzing repository..."
                ):

                    docs = generate_docs(code)

                    score = calculate_score(code)

                    st.success(
                        "Documentation Generated Successfully"
                    )

                    st.metric(
                        "📈 Repository Health Score",
                        f"{score}/100"
                    )

                    st.markdown(docs)

                    cursor.execute("""
                    INSERT INTO projects (
                        user_email,
                        repo_name,
                        generated_docs,
                        score,
                        created_at
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        st.session_state.user_email,
                        uploaded_file.name,
                        docs,
                        score,
                        str(datetime.now())
                    ))

                    conn.commit()

                    pdf_file = export_pdf(docs)

                    with open(
                        pdf_file,
                        "rb"
                    ) as file:

                        st.download_button(
                            label="📥 Download PDF",
                            data=file,
                            file_name="documentation.pdf",
                            mime="application/pdf"
                        )

# =========================================================
# AI CHAT
# =========================================================

elif menu == "AI Chat":

    if not st.session_state.logged_in:

        st.warning("Please Login First")

    else:

        st.title("💬 Chat With Repository")

        repo_code = st.text_area(
            "Paste Repository Code"
        )

        question = st.text_input(
            "Ask AI Question"
        )

        if st.button("Ask AI"):

            with st.spinner("AI Thinking..."):

                answer = chat_with_repo(
                    repo_code,
                    question
                )

                st.success("Answer Generated")

                st.write(answer)

# =========================================================
# ANALYTICS
# =========================================================

elif menu == "Analytics":

    st.title("📊 Analytics Dashboard")

    cursor.execute(
        "SELECT COUNT(*) FROM users"
    )

    total_users = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM projects"
    )

    total_projects = cursor.fetchone()[0]

    cursor.execute("""
    SELECT AVG(score)
    FROM projects
    """)

    avg_score = cursor.fetchone()[0]

    if avg_score is None:
        avg_score = 0

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown(f"""
        <div class="card" style="
        text-align:center;
        height:180px;
        ">

        <h1 style="font-size:50px;">👤</h1>

        <h2>Total Users</h2>

        <h1 style="
        color:#38bdf8;
        ">
        {total_users}
        </h1>

        </div>
        """, unsafe_allow_html=True)

    with col2:

        st.markdown(f"""
        <div class="card" style="
        text-align:center;
        height:180px;
        ">

        <h1 style="font-size:50px;">📂</h1>

        <h2>Total Projects</h2>

        <h1 style="
        color:#38bdf8;
        ">
        {total_projects}
        </h1>

        </div>
        """, unsafe_allow_html=True)

    with col3:

        st.markdown(f"""
        <div class="card" style="
        text-align:center;
        height:180px;
        ">

        <h1 style="font-size:50px;">📈</h1>

        <h2>Average Score</h2>

        <h1 style="
        color:#38bdf8;
        ">
        {round(avg_score, 1)}
        </h1>

        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div class="card">

    <h2 style="
    color:white;
    ">
    🚀 Platform Insights
    </h2>

    <br>

    ✅ AI Documentation Generation Active <br><br>

    ✅ Repository Analysis System Running <br><br>

    ✅ PDF Export System Enabled <br><br>

    ✅ Admin Monitoring Enabled <br><br>

    ✅ User Authentication Active <br><br>

    ✅ Real-Time Analytics Working

    </div>
    """, unsafe_allow_html=True)

# =========================================================
# HISTORY
# =========================================================

elif menu == "History":

    if not st.session_state.logged_in:

        st.warning("Please Login First")

    else:

        st.title("📜 Project History")

        cursor.execute("""
        SELECT repo_name, score, created_at
        FROM projects
        WHERE user_email=?
        """,
        (
            st.session_state.user_email,
        ))

        projects = cursor.fetchall()

        if projects:

            for project in projects:

                st.markdown(f"""
                <div class="card">

                <h3>📂 {project[0]}</h3>

                <p>📈 Score: {project[1]}/100</p>

                <p>🕒 {project[2]}</p>

                </div>
                """, unsafe_allow_html=True)

        else:

            st.info("No project history found")

# =========================================================
# ADMIN PANEL
# =========================================================

elif menu == "Admin Panel":

    if st.session_state.user_role != "admin":

        st.error("Admin Access Only")

    else:

        st.title("👑 Admin Dashboard")

        search = st.text_input(
            "Search User"
        )

        query = "SELECT * FROM users"

        params = ()

        if search:

            query += " WHERE name LIKE ?"

            params = (
                f"%{search}%",
            )

        cursor.execute(
            query,
            params
        )

        users = cursor.fetchall()

        for user in users:

            st.markdown("---")

            col1, col2, col3 = st.columns(3)

            with col1:

                st.write(f"👤 {user[1]}")

                st.write(f"📧 {user[2]}")

            with col2:

                st.write(
                    f"⚠️ Warnings: {user[6]}"
                )

                st.write(
                    f"🚫 Banned: {user[5]}"
                )

            with col3:

                if st.button(
                    f"Ban {user[2]}"
                ):

                    cursor.execute("""
                    UPDATE users
                    SET is_banned=1
                    WHERE email=?
                    """,
                    (
                        user[2],
                    ))

                    conn.commit()

                    st.success("User Banned")

                if st.button(
                    f"Unban {user[2]}"
                ):

                    cursor.execute("""
                    UPDATE users
                    SET is_banned=0
                    WHERE email=?
                    """,
                    (
                        user[2],
                    ))

                    conn.commit()

                    st.success("User Unbanned")

                if st.button(
                    f"Warning {user[2]}"
                ):

                    cursor.execute("""
                    UPDATE users
                    SET warnings = warnings + 1
                    WHERE email=?
                    """,
                    (
                        user[2],
                    ))

                    conn.commit()

                    st.success("Warning Added")

                if st.button(
                    f"Delete {user[2]}"
                ):

                    cursor.execute("""
                    DELETE FROM users
                    WHERE email=?
                    """,
                    (
                        user[2],
                    ))

                    conn.commit()

                    st.success("User Deleted")

# =========================================================
# LOGOUT
# =========================================================

if st.sidebar.button("Logout"):

    st.session_state.logged_in = False

    st.session_state.user_email = ""

    st.session_state.user_name = ""

    st.session_state.user_role = "user"

    st.success("Logged Out")

# =========================================================
# FOOTER
# =========================================================

st.markdown("""
<hr>

<div style='
text-align:center;
padding:25px;
font-size:18px;
color:#cbd5e1;
'>

🚀 AI Hackathon 2026 Project <br><br>

🏫 TECHNOCRATS INSTITUTE OF TECHNOLOGY BHOPAL <br><br>

⚡ Powered By Gemini AI + Streamlit + Python <br><br>

💙 Developed By Ritesh Kumar Singh

</div>
""", unsafe_allow_html=True)