import streamlit as st
import requests
import pandas as pd
from datetime import datetime

API_URL = "http://3.22.241.80"

def login_page():
    st.title("JobHunt - Login")
    if not st.session_state.get("show_register", False):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            response = requests.post(f"{API_URL}/token", data={"username": username, "password": password})
            if response.status_code == 200:
                st.session_state["token"] = response.json()["access_token"]
                st.session_state["show_register"] = False
                st.success("Logged in!")
                st.rerun()
            else:
                st.error("Invalid credentials")
        if st.button("Go to Register"):
            st.session_state["show_register"] = True
            st.rerun()
    else:
        register_page()

def register_page():
    st.title("JobHunt - Register")
    username = st.text_input("New Username")
    password = st.text_input("New Password", type="password")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Register"):
            response = requests.post(f"{API_URL}/register", json={"username": username, "password": password})
            if response.status_code == 201:
                st.success("Registered! Please log in.")
                st.session_state["show_register"] = False
                st.rerun()
            else:
                st.error("Registration failed")
    with col2:
        if st.button("Back to Login"):
            st.session_state["show_register"] = False
            st.rerun()

def logout():
    st.session_state.pop("token", None)
    st.session_state["show_register"] = False
    st.success("Logged out!")
    st.rerun()

def jobs_page():
    st.header("Manage Jobs")
    token = st.session_state.get("token")
    if not token:
        st.error("Please log in")
        return

    headers = {"Authorization": f"Bearer {token}"}

    st.subheader("Add Job")
    with st.form("add_job"):
        company = st.text_input("Company")
        position = st.text_input("Position")
        status = st.selectbox("Status", ["applied", "under consideration", "rejected", "ghosted"])
        if st.form_submit_button("Add Job"):
            payload = {"company": company, "position": position, "status": status}
            response = requests.post(f"{API_URL}/jobs", json=payload, headers=headers)
            if response.status_code == 200:
                st.success("Job added")
            else:
                st.error(f"Error: {response.json().get('detail')}")

    response = requests.get(f"{API_URL}/jobs", headers=headers)
    if response.status_code == 200:
        jobs = response.json()
        if jobs:
            df = pd.DataFrame(jobs)
            st.dataframe(df[["display_id", "company", "position", "status"]].rename(columns={"display_id": "ID"}))
        else:
            st.write("No jobs found")

    st.subheader("Update or Delete Job")
    job_display_id = st.number_input("Job ID to update/delete", min_value=1, step=1)
    col1, col2 = st.columns(2)
    with col1:
        new_status = st.selectbox("Update Status", ["applied", "under consideration", "rejected", "ghosted"], key="job_status")
        if st.button("Update Status"):
            payload = {"status": new_status}
            response = requests.patch(f"{API_URL}/jobs/{job_display_id}", json=payload, headers=headers)
            if response.status_code == 200:
                st.success("Status updated")
            else:
                st.error(f"Error: {response.json().get('detail')}")
    with col2:
        if st.button("Delete Job"):
            response = requests.delete(f"{API_URL}/jobs/{job_display_id}", headers=headers)
            if response.status_code == 204:
                st.success("Job deleted")
            else:
                st.error(f"Error: {response.json().get('detail')}")

def interviews_page():
    st.header("Manage Interviews")
    token = st.session_state.get("token")
    if not token:
        st.error("Please log in")
        return

    headers = {"Authorization": f"Bearer {token}"}

    st.subheader("Add Interview")
    with st.form("add_interview"):
        job_display_id = st.number_input("Job ID", min_value=1, step=1)
        date = st.text_input("Date (YYYY-MM-DD)", "2025-04-29")
        time = st.text_input("Time (HH:MM)", "14:00")
        details = st.text_input("Details", "Phone Interview")
        if st.form_submit_button("Add Interview"):
            payload = {"job_display_id": job_display_id, "date": date, "time": time, "details": details}
            response = requests.post(f"{API_URL}/interviews", json=payload, headers=headers)
            if response.status_code == 200:
                st.success("Interview added")
            else:
                st.error(f"Error: {response.json().get('detail')}")

    response = requests.get(f"{API_URL}/interviews", headers=headers)
    if response.status_code == 200:
        interviews = response.json()
        if interviews:
            df = pd.DataFrame(interviews)
            st.dataframe(df[["display_id", "job_display_id", "date", "time", "details"]].rename(columns={"display_id": "ID", "job_display_id": "Job ID"}))
        else:
            st.write("No interviews found")

    st.subheader("Update or Delete Interview")
    interview_display_id = st.number_input("Interview ID to update/delete", min_value=1, step=1)
    col1, col2 = st.columns(2)
    with col1:
        with st.form("update_interview"):
            new_job_display_id = st.number_input("New Job ID", min_value=1, step=1)
            new_date = st.text_input("New Date (YYYY-MM-DD)", "2025-04-30")
            new_time = st.text_input("New Time (HH:MM)", "15:00")
            new_details = st.text_input("New Details", "In-Person Interview")
            if st.form_submit_button("Update Interview"):
                payload = {"job_display_id": new_job_display_id, "date": new_date, "time": new_time, "details": new_details}
                response = requests.patch(f"{API_URL}/interviews/{interview_display_id}", json=payload, headers=headers)
                if response.status_code == 200:
                    st.success("Interview updated")
                else:
                    st.error(f"Error: {response.json().get('detail')}")
    with col2:
        if st.button("Delete Interview"):
            response = requests.delete(f"{API_URL}/interviews/{interview_display_id}", headers=headers)
            if response.status_code == 204:
                st.success("Interview deleted")
            else:
                st.error(f"Error: {response.json().get('detail')}")

def calendar_page():
    st.header("Calendar")
    token = st.session_state.get("token")
    if not token:
        st.error("Please log in")
        return

    headers = {"Authorization": f"Bearer {token}"}

    st.subheader("Add Calendar Event")
    with st.form("add_event"):
        event_type = st.selectbox("Event Type", ["job", "interview"])
        date = st.text_input("Date (YYYY-MM-DD)", "2025-04-29")
        time = st.text_input("Time (HH:MM)", "14:00")
        details = st.text_input("Details", "Application Deadline")
        if st.form_submit_button("Add Event"):
            payload = {"type": event_type, "date": date, "time": time, "details": details}
            response = requests.post(f"{API_URL}/calendar", json=payload, headers=headers)
            if response.status_code == 200:
                st.success("Event added")
            else:
                st.error(f"Error: {response.json().get('detail')}")

    response = requests.get(f"{API_URL}/calendar", headers=headers)
    if response.status_code == 200:
        events = response.json()
        if events:
            df = pd.DataFrame(events)
            st.dataframe(df[["display_id", "type", "date", "time", "details"]].rename(columns={"display_id": "ID"}))
        else:
            st.write("No calendar events found")

    st.subheader("Update or Delete Calendar Event")
    event_display_id = st.number_input("Event ID to update/delete", min_value=1, step=1)
    col1, col2 = st.columns(2)
    with col1:
        with st.form("update_event"):
            new_type = st.selectbox("Event Type", ["job", "interview"], key="event_type")
            new_date = st.text_input("New Date (YYYY-MM-DD)", "2025-04-30")
            new_time = st.text_input("New Time (HH:MM)", "15:00")
            new_details = st.text_input("New Details", "Application Deadline")
            if st.form_submit_button("Update Event"):
                payload = {"type": new_type, "date": new_date, "time": new_time, "details": new_details}
                response = requests.patch(f"{API_URL}/calendar/{event_display_id}", json=payload, headers=headers)
                if response.status_code == 200:
                    st.success("Event updated")
                else:
                    st.error(f"Error: {response.json().get('detail')}")
    with col2:
        if st.button("Delete Event"):
            response = requests.delete(f"{API_URL}/calendar/{event_display_id}", headers=headers)
            if response.status_code == 204:
                st.success("Event deleted")
            else:
                st.error(f"Error: {response.json().get('detail')}")

def main():
    if "token" not in st.session_state:
        login_page()
    else:
        st.sidebar.button("Logout", on_click=logout)
        page = st.sidebar.selectbox("Select Page", ["Jobs", "Interviews", "Calendar"])
        if page == "Jobs":
            jobs_page()
        elif page == "Interviews":
            interviews_page()
        elif page == "Calendar":
            calendar_page()

if __name__ == "__main__":
    main()