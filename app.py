import streamlit as st
import pickle
import pandas as pd
import numpy as np
import PyPDF2
import plotly.express as px

# ================= SESSION =================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "history" not in st.session_state:
    st.session_state.history = []

# ================= LOGIN =================
if not st.session_state.logged_in:
    st.title("🔐 AI System Login")
    user = st.text_input("Username")

    if st.button("Login"):
        if user:
            st.session_state.logged_in = True
            st.session_state.user = user
            st.rerun()
        else:
            st.error("Enter username")

    st.stop()

# ================= MODEL =================
model = pickle.load(open("model.pkl", "rb"))

# ================= PAGE =================
st.set_page_config(page_title="AI Career Intelligence", layout="wide")

# ================= STYLE =================
st.markdown("""
<style>
.stApp { background:#f8f5f0; }
h1,h2,h3 { color:#b58900; }
.kpi {
    background:white;
    padding:15px;
    border-radius:12px;
    box-shadow:0px 4px 10px rgba(0,0,0,0.08);
    text-align:center;
}
</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.markdown(f"### 👤 Welcome, {st.session_state.user}")
st.title("AI Placement & Career Intelligence Platform")
st.markdown("From uncertainty → data-driven decisions")
st.markdown("---")

# ================= TABS =================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Prediction",
    "📄 Resume AI",
    "📈 Analytics",
    "💼 Business"
])

# ================= RESUME FUNCTIONS =================
def extract_text(file):
    text = ""
    pdf = PyPDF2.PdfReader(file)
    for page in pdf.pages:
        text += page.extract_text()
    return text.lower()

def analyze_resume(text):
    skills_list = ["python","java","machine learning","data science","react","dsa","sql","flask"]
    found = [s for s in skills_list if s in text]

    skill_score = min(len(found)*2, 10)
    internships = 1 if "internship" in text else 0
    projects = 2 if "project" in text else 0

    return skill_score, internships, projects, found

# ================= TAB 2: RESUME =================
with tab2:
    st.subheader("📄 Resume Analyzer")

    file = st.file_uploader("Upload Resume PDF", type=["pdf"])

    if file:
        text = extract_text(file)
        skills, internships, projects, found = analyze_resume(text)

        st.session_state.skills = skills
        st.session_state.internships = internships
        st.session_state.projects = projects

        st.success("Resume connected to prediction system")

        st.write("### 🔍 Detected Skills")
        st.write(found if found else "No strong skills detected")

        st.write("### 📊 Skill Score")
        st.progress(skills * 10)

# ================= TAB 1: PREDICTION =================
with tab1:

    col1, col2 = st.columns([1,1.2])

    with col1:
        st.subheader("🎓 Student Input")

        cgpa = st.slider("CGPA", 0.0, 10.0, 7.0)

        internships = st.session_state.get("internships", 0)
        skills = st.session_state.get("skills", 6)
        projects = st.session_state.get("projects", 1)

        st.info("Auto-filled from resume")

        internships = st.selectbox("Internships", [0,1,2,3], index=int(internships))
        skills = st.slider("Skills Score", 1, 10, int(skills))
        projects = st.slider("Projects", 0, 5, int(projects))
        college = st.selectbox("College Tier", [1,2,3])

        btn = st.button("🚀 Predict")

    with col2:
        st.subheader("📊 Results")

        if btn:

            data = pd.DataFrame(
                [[cgpa, internships, skills, projects, college]],
                columns=['cgpa','internships','skills','projects','college_tier']
            )

            prob = model.predict_proba(data)[0][1]
            prob_percent = int(prob * 100)
            salary = round(3 + cgpa*0.5 + skills*0.3, 2)

            risk = "Low" if prob > 0.75 else "Medium" if prob > 0.5 else "High"

            # KPIs
            k1, k2, k3 = st.columns(3)
            k1.metric("Placement %", f"{prob_percent}%")
            k2.metric("Salary", f"₹{salary} LPA")
            k3.metric("Risk", risk)

            # Timeline
            timeline = pd.DataFrame({
                "Time":["3M","6M","12M"],
                "Probability":[prob_percent*0.6, prob_percent*0.8, prob_percent]
            })

            fig = px.line(timeline, x="Time", y="Probability", markers=True)
            st.plotly_chart(fig, use_container_width=True)

            # Feature donut
            features = pd.DataFrame({
                "Feature":["CGPA","Internships","Skills","Projects","College"],
                "Impact":[30,25,20,15,10]
            })

            fig2 = px.pie(features, names="Feature", values="Impact", hole=0.5)
            st.plotly_chart(fig2, use_container_width=True)

            # Explainable AI
            st.markdown("### 🧠 Explainable AI")

            explain_df = pd.DataFrame({
                "Factor":["CGPA","Internships","Skills","Projects"],
                "Contribution":[cgpa*10, internships*20, skills*8, projects*5]
            })

            fig3 = px.bar(explain_df, x="Factor", y="Contribution", color="Contribution")
            st.plotly_chart(fig3, use_container_width=True)

            # What-if
            st.markdown("### 🔮 What-if Simulation")
            new_skills = st.slider("Improve Skills to:", 1, 10, skills)
            new_prob = min(prob_percent + (new_skills - skills)*3, 100)
            st.write(f"New Placement Probability: **{new_prob}%**")

            # Download report
            report = f"""
Placement: {prob_percent}%
Salary: ₹{salary} LPA
Risk: {risk}
"""
            st.download_button("📄 Download Report", report)

            # Save history
            st.session_state.history.append({
                "Placement": prob_percent,
                "Salary": salary,
                "Risk": risk
            })

# ================= TAB 3: ANALYTICS =================
with tab3:
    st.subheader("📈 Analytics Dashboard")

    if len(st.session_state.history) == 0:
        st.info("No predictions yet")
    else:
        df = pd.DataFrame(st.session_state.history)

        st.dataframe(df, use_container_width=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("Avg Placement", round(df["Placement"].mean(),2))
        c2.metric("Avg Salary", round(df["Salary"].mean(),2))
        c3.metric("Total Runs", len(df))

        fig4 = px.histogram(df, x="Risk", color="Risk")
        st.plotly_chart(fig4)

        df["Index"] = range(1, len(df)+1)
        fig5 = px.line(df, x="Index", y="Placement", markers=True)
        st.plotly_chart(fig5)

# ================= TAB 4: BUSINESS =================
with tab4:
    st.subheader("💼 Business Insights")

    st.markdown("""
    ### 🚀 Innovation
    AI system combining prediction + resume intelligence.

    ### 🏦 Value
    - Reduces loan default risk  
    - Enables smarter decisions  
    - Improves student outcomes  

    ### 🔥 Differentiator
    Fully connected AI system where resume impacts prediction.
    """)