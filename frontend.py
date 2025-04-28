import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from streamlit_calendar import calendar
import json

st.title("JobHunt: Job Application Tracker")

# Session state for user
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = None

# API base URL
API_URL = "http://3.22.241.80"

# Login/Register
if not st.session_state.user_id:
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.header("Login")
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            try:
                response = requests.post(f"{API_URL}/login", json={"username": login_username, "password": login_password}, timeout=5)
                if response.status_code == 200:
                    st.session_state.user_id = response.json()["user_id"]
                    st.session_state.username = login_username
                    st.success("Logged in!")
                    st.rerun()
                else:
                    st.error(f"Error: {response.json()['detail']}")
            except requests.exceptions.RequestException as e:
                st.error(f"Failed to connect to backend: {str(e)}")
    
    with tab2:
        st.header("Register")
        reg_username = st.text_input("Username", key="reg_username")
        reg_password = st.text_input("Password", type="password", key="reg_password")
        if st.button("Register"):
            try:
                response = requests.post(f"{API_URL}/register", json={"username": reg_username, "password": reg_password}, timeout=5)
                if response.status_code == 200:
                    st.success("Registered! Please login.")
                else:
                    st.error(f"Error: {response.json()['detail']}")
            except requests.exceptions.RequestException as e:
                st.error(f"Failed to connect to backend: {str(e)}")
else:
    st.header(f"Welcome, {st.session_state.username}!")
    if st.button("Logout"):
        st.session_state.user_id = None
        st.session_state.username = None
        st.rerun()
    
    # Job Management
    st.subheader("Add Job")
    company = st.text_input("Company")
    job_title = st.text_input("Job Title")
    job_description = st.text_area("Job Description", max_chars=10000)
    role = st.text_input("Role")
    if st.button("Add Job"):
        try:
            response = requests.post(
                f"{API_URL}/jobs?user_id={st.session_state.user_id}",
                json={"company": company, "job_title": job_title, "job_description": job_description, "role": role},
                timeout=5
            )
            if response.status_code == 200:
                st.success(f"Job added with status: {response.json()['status']} (Job ID: {response.json()['job_id']})")
            else:
                st.error(f"Error: {response.json()['detail']}")
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to add job: {str(e)}")
    
    # View All Jobs
    st.subheader("Your Jobs")
    try:
        response = requests.get(f"{API_URL}/jobs?user_id={st.session_state.user_id}", timeout=5)
        if response.status_code == 200:
            jobs = response.json()
            if jobs:
                df = pd.DataFrame(jobs)
                df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
                st.dataframe(
                    df[['job_id', 'company', 'job_title', 'role', 'status', 'created_at']],
                    column_config={
                        "job_id": "Job ID",
                        "company": "Company",
                        "job_title": "Job Title",
                        "role": "Role",
                        "status": "Status",
                        "created_at": "Created At"
                    },
                    hide_index=True
                )
            else:
                st.info("No jobs added yet.")
        else:
            st.error(f"Error: {response.json()['detail']}")
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch jobs: {str(e)}")
    
    # Interview Scheduling
    st.subheader("Schedule Interview")
    job_id = st.number_input("Job ID", min_value=1, step=1)
    date_time = st.text_input("Date and Time (YYYY-MM-DD HH:MM)", "2025-05-01 10:00")
    if st.button("Schedule Interview"):
        try:
            response = requests.post(
                f"{API_URL}/interviews?user_id={st.session_state.user_id}",
                json={"job_id": job_id, "date_time": date_time},
                timeout=5
            )
            if response.status_code == 200:
                st.success("Interview scheduled")
            else:
                st.error(f"Error: {response.json()['detail']}")
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to schedule interview: {str(e)}")
    
    # Interview Calendar
    st.subheader("Your Interview Schedule")
    try:
        response = requests.get(f"{API_URL}/interviews?user_id={st.session_state.user_id}", timeout=5)
        if response.status_code == 200:
            interviews = response.json()
            if interviews:
                events = [
                    {
                        "title": f"Interview for Job ID {i['job_id']}",
                        "start": i['date_time'].replace("T", " ")[:16],
                        "end": i['date_time'].replace("T", " ")[:16]
                    }
                    for i in interviews
                ]
                calendar_options = {
                    "headerToolbar": {
                        "left": "prev,next today",
                        "center": "title",
                        "right": "dayGridMonth,timeGridWeek,timeGridDay"
                    },
                    "initialView": "dayGridMonth",
                    "events": events
                }
                calendar(events=events, options=calendar_options)
            else:
                st.info("No interviews scheduled yet.")
        else:
            st.error(f"Error: {response.json()['detail']}")
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch interviews: {str(e)}")
    
    # Interview Prep
    st.subheader("Get Interview Prep")
    prep_job_id = st.number_input("Job ID for Prep", min_value=1, step=1)
    if st.button("Get Prep"):
        try:
            response = requests.get(f"{API_URL}/interview-prep/{prep_job_id}?user_id={st.session_state.user_id}", timeout=5)
            if response.status_code == 200:
                st.markdown(response.json()["prep_content"])
            else:
                st.error(f"Error: {response.json()['detail']}")
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to get prep: {str(e)}")