import streamlit as st
import pandas as pd
from datetime import time

st.set_page_config(layout="wide")  # Use full screen width

st.title("IP Address Usage Checker for Students")

uploaded_logs = st.file_uploader("Upload logs CSV file", type=["csv"])

use_student_list = st.toggle("Use student list", value=False)

student_text = ""
if use_student_list:
    student_text = st.text_area("Paste student list (one name per line)")

start_time = st.time_input("Start time", value=time(9, 0))
end_time = st.time_input("End time", value=time(12, 0))

group_by_ip = st.checkbox("Group logs by IP address", value=True)

if uploaded_logs:
    # Read CSV logs
    df = pd.read_csv(uploaded_logs, sep=',', low_memory=False)
    df['Date'] = pd.to_datetime(df['Time'], format="%y/%m/%d, %H:%M:%S").dt.date
    df['Time'] = pd.to_datetime(df['Time'], format="%y/%m/%d, %H:%M:%S").dt.time
    cols = ['Date'] + [col for col in df.columns if col != 'Date']
    df = df[cols]

    # Filter by time
    df = df[(df['Time'] >= start_time) & (df['Time'] <= end_time)]

    # Filter by student list if enabled
    if use_student_list:
        student_list = [line.strip() for line in student_text.splitlines() if line.strip()]
        if student_list:
            df = df[df['User full name'].isin(student_list)]

    # Count unique IPs per user
    ip_counts = df.groupby("User full name")["IP address"].nunique()
    users_with_multiple_ips = ip_counts[ip_counts > 1]

    if users_with_multiple_ips.empty:
        st.success("No users found with more than one IP address in the selected time frame.")
    else:
        st.warning(f"Found {len(users_with_multiple_ips)} user(s) with multiple IP addresses.")

        actual_ips = df[df["User full name"].isin(users_with_multiple_ips.index)].groupby("User full name")["IP address"].unique()

        # Show users with multiple IPs and count in brackets
        for user in users_with_multiple_ips.index:
            num_ips = ip_counts[user]
            st.subheader(f"{user} ({num_ips} IP{'s' if num_ips > 1 else ''})")

            if group_by_ip:
                ips = actual_ips[user]
                for ip in ips:
                    st.markdown(f"**IP:** {ip}")
                    user_ip_logs = df[(df['User full name'] == user) & (df['IP address'] == ip)]
                    st.dataframe(user_ip_logs)
                    st.write("---")
            else:
                user_logs = df[df['User full name'] == user]
                st.dataframe(user_logs)
                st.write("---")
else:
    st.info("Please upload the logs CSV file.")
