# app.py

import os
import re
import sqlite3
import datetime
import streamlit as st
from typing import List, Dict

# Streamlit configuration
st.set_page_config(page_title="Job Search AI Agent", page_icon="🔍", layout="wide")
st.title("🔍 Job Search AI Agent (Public APIs Only)")
st.markdown("---")

def search_github_jobs(query: str, location: str = "") -> List[Dict]:
    jobs = []
    try:
        sample_jobs = [
            {
                "title": f"{query} Developer",
                "company": "Tech Company A",
                "location": location or "Remote",
                "description": f"Looking for experienced {query} developer",
                "url": "https://example.com/job/1",
                "posted_date": "2025-06-01",
                "skills": [query.lower(), "python", "javascript"]
            },
            {
                "title": f"Senior {query}",
                "company": "Startup B",
                "location": location or "San Francisco, CA",
                "description": f"Senior {query} position with growth opportunities",
                "url": "https://example.com/job/2",
                "posted_date": "2025-06-02",
                "skills": [query.lower(), "react", "node.js"]
            }
        ]
        return sample_jobs
    except Exception as e:
        st.error(f"Error fetching jobs: {e}")
        return []

def search_public_job_sites(query: str, location: str = "") -> List[Dict]:
    mock_jobs = [
        {
            "title": f"{query} Specialist",
            "company": "Public Corp",
            "location": location or "New York, NY",
            "description": f"We are hiring for {query} position",
            "salary": "$70,000 - $90,000",
            "posted_date": datetime.date.today().strftime("%Y-%m-%d"),
            "source": "PublicJobs.com"
        },
        {
            "title": f"Junior {query}",
            "company": "Open Source Inc",
            "location": location or "Remote",
            "description": f"Entry level {query} opportunity",
            "salary": "$50,000 - $65,000",
            "posted_date": datetime.date.today().strftime("%Y-%m-%d"),
            "source": "FreeJobBoard.org"
        }
    ]
    return mock_jobs

def get_company_info(company_name: str) -> Dict:
    return {
        "name": company_name,
        "industry": "Technology",
        "size": "50-200 employees",
        "website": f"https://{company_name.lower().replace(' ', '')}.com",
        "description": f"{company_name} is a growing technology company."
    }

def simple_resume_parser(resume_text: str) -> Dict:
    try:
        skills_keywords = [
            'python', 'javascript', 'java', 'react', 'node.js', 'sql',
            'html', 'css', 'aws', 'docker', 'kubernetes', 'git',
            'machine learning', 'data science', 'ui/ux', 'design'
        ]
        text_lower = resume_text.lower()
        found_skills = [skill for skill in skills_keywords if skill in text_lower]
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, resume_text)
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, resume_text)
        return {
            "skills": found_skills,
            "email": emails[0] if emails else "Not found",
            "phone": phones[0] if phones else "Not found",
            "text_length": len(resume_text),
            "word_count": len(resume_text.split())
        }
    except Exception as e:
        return {"error": f"Error parsing resume: {e}"}

def init_db():
    try:
        conn = sqlite3.connect('job_search.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS saved_jobs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT,
                        company TEXT,
                        location TEXT,
                        description TEXT,
                        url TEXT,
                        saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        c.execute('''CREATE TABLE IF NOT EXISTS applications (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        job_title TEXT,
                        company TEXT,
                        status TEXT DEFAULT 'Applied',
                        applied_date DATE,
                        notes TEXT)''')
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Database error: {e}")
        return False

def save_job(job_data: Dict):
    try:
        conn = sqlite3.connect('job_search.db')
        c = conn.cursor()
        c.execute("""INSERT INTO saved_jobs (title, company, location, description, url)
                     VALUES (?, ?, ?, ?, ?)""",
                  (job_data.get('title', ''), job_data.get('company', ''),
                   job_data.get('location', ''), job_data.get('description', ''),
                   job_data.get('url', '')))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error saving job: {e}")
        return False

def get_saved_jobs():
    try:
        conn = sqlite3.connect('job_search.db')
        c = conn.cursor()
        c.execute("SELECT * FROM saved_jobs ORDER BY saved_at DESC")
        jobs = c.fetchall()
        conn.close()
        return jobs
    except Exception as e:
        st.error(f"Error retrieving jobs: {e}")
        return []

# Initialize DB
init_db()

# --- UI Tabs ---
tab1, tab2, tab3, tab4 = st.tabs(["🔍 Job Search", "📄 Resume Analysis", "💾 Saved Jobs", "📊 Dashboard"])

with tab1:
    st.subheader("Search for Jobs (Public Sources)")
    col1, col2 = st.columns(2)
    with col1:
        job_role = st.text_input("Job Role", placeholder="e.g., Python Developer")
    with col2:
        job_location = st.text_input("Location (optional)", placeholder="e.g., Remote, NYC")

    search_type = st.selectbox("Search Method", ["Mock Data (Demo)", "Public Job Boards", "Company Websites"])

    if st.button("🔎 Search Jobs", type="primary"):
        if not job_role:
            st.warning("Please enter a job role.")
        else:
            with st.spinner("Searching public job sources..."):
                jobs = []
                if search_type == "Mock Data (Demo)":
                    jobs = search_github_jobs(job_role, job_location)
                    jobs.extend(search_public_job_sites(job_role, job_location))
                else:
                    jobs = search_public_job_sites(job_role, job_location)

                if jobs:
                    st.subheader(f"Found {len(jobs)} job opportunities")
                    for i, job in enumerate(jobs):
                        with st.expander(f"{job.get('title', 'N/A')} at {job.get('company', 'N/A')}"):
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.write(f"**Company:** {job.get('company', 'N/A')}")
                                st.write(f"**Location:** {job.get('location', 'N/A')}")
                                st.write(f"**Description:** {job.get('description', 'N/A')}")
                                if 'salary' in job:
                                    st.write(f"**Salary:** {job.get('salary')}")
                                if 'skills' in job:
                                    st.write(f"**Skills:** {', '.join(job.get('skills', []))}")
                            with col2:
                                if st.button(f"💾 Save Job", key=f"save_{i}"):
                                    if save_job(job):
                                        st.success("Job saved!")
                                if job.get('url'):
                                    st.markdown(f"[🔗 Apply]({job.get('url')})")
                else:
                    st.info("No jobs found. Try a different search term.")

with tab2:
    st.subheader("Resume Analysis (No External APIs)")
    resume_input = st.text_area("Paste your resume text here:", height=300)
    if st.button("📊 Analyze Resume"):
        if resume_input.strip():
            with st.spinner("Analyzing resume..."):
                analysis = simple_resume_parser(resume_input)
                if "error" not in analysis:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("📧 Contact Info")
                        st.write(f"**Email:** {analysis.get('email', 'Not found')}")
                        st.write(f"**Phone:** {analysis.get('phone', 'Not found')}")
                    with col2:
                        st.subheader("📊 Document Stats")
                        st.write(f"**Word Count:** {analysis.get('word_count', 0)}")
                        st.write(f"**Character Count:** {analysis.get('text_length', 0)}")
                    st.subheader("🛠️ Skills Found")
                    skills = analysis.get('skills', [])
                    if skills:
                        for skill in skills:
                            st.markdown(f"- {skill.title()}")
                    else:
                        st.info("No common technical skills detected.")
                else:
                    st.error(analysis["error"])
        else:
            st.warning("Please paste your resume text.")

with tab3:
    st.subheader("💾 Saved Jobs")
    saved_jobs = get_saved_jobs()
    if saved_jobs:
        for job in saved_jobs:
            with st.expander(f"{job[1]} at {job[2]}"):
                st.write(f"**Company:** {job[2]}")
                st.write(f"**Location:** {job[3]}")
                st.write(f"**Description:** {job[4]}")
                st.write(f"**Saved:** {job[6]}")
                if job[5]:
                    st.markdown(f"[🔗 View Job]({job[5]})")
    else:
        st.info("No saved jobs yet. Search and save jobs from the Search tab.")

with tab4:
    st.subheader("📊 Job Search Dashboard")
    saved_count = len(get_saved_jobs())
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Saved Jobs", saved_count)
    with col2:
        st.metric("Public APIs Used", "0")
    with col3:
        st.metric("No Auth Required", "✅")

    st.subheader("🔧 Available Features")
    features = [
        "✅ Job search using public sources",
        "✅ Basic resume text analysis",
        "✅ Local job saving (SQLite)",
        "✅ Simple company lookup",
        "❌ Advanced AI search (requires API keys)",
        "❌ Professional resume parsing (requires API keys)",
        "❌ Calendar integration (requires Google API)",
        "❌ Email notifications (requires email API)"
    ]
    for feature in features:
        st.write(feature)

# Sidebar
with st.sidebar:
    st.header("🌟 Public APIs Only")
    st.success("✅ No API Keys Required")
    st.success("✅ No Authentication Needed")
    st.success("✅ Works Out of the Box")
    st.markdown("---")
    st.subheader("📚 Public Resources Used:")
    st.write("• Local SQLite database")
    st.write("• Text processing libraries")
    st.write("• Mock job data for demo")
    st.write("• Basic regex patterns")
    st.markdown("---")
    st.subheader("🔄 To Add Real APIs:")
    st.write("• JSearch API (RapidAPI)")
    st.write("• Reed Jobs API")
    st.write("• Adzuna API")
    st.write("• The Muse API")
    st.write("• GitHub Jobs alternatives")
    st.info("💡 Many job APIs require registration but offer free tiers!")

