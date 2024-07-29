import streamlit as st
import pandas as pd
import hashlib
import json
from datetime import datetime
from functions import (
    get_latest_date,
    load_users,
    save_users,
    ensure_default_admin
)
from productivity_calendar import productivity_calendar

# Set Streamlit page configuration to wide layout
st.set_page_config(page_title="Productivity Dashboard", layout="wide")

# Initialize session state variables
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'current_user' not in st.session_state:
    st.session_state['current_user'] = None
if 'users_df' not in st.session_state:
    st.session_state['users_df'] = load_users()
    st.session_state['users_df'] = ensure_default_admin(st.session_state['users_df'])  # Ensure default admin account is created
if 'is_admin' not in st.session_state:
    st.session_state['is_admin'] = False
if 'admin_authenticated' not in st.session_state:
    st.session_state['admin_authenticated'] = False
if 'show_change_password' not in st.session_state:
    st.session_state['show_change_password'] = False

# Function for user registration
def register():
    st.title("Register")
    email = st.text_input("Enter your email address")
    password = st.text_input("Enter your password", type="password")
    confirm_password = st.text_input("Confirm your password", type="password")

    if st.button("Register", key="register_button"):
        if password == confirm_password:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            new_user = pd.DataFrame({'email': [email], 'password': [hashed_password], 'approved': [False], 'role': ['user']})
            st.session_state.users_df = pd.concat([st.session_state.users_df, new_user], ignore_index=True)
            save_users(st.session_state.users_df)
            st.success("Registration successful! Please wait for admin approval.")
        else:
            st.error("Passwords do not match.")

# Function for user login
def login():
    st.title("Login")
    email = st.text_input("Enter your email address")
    password = st.text_input("Enter your password", type="password")

    if st.button("Login", key="login_button"):
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        user = st.session_state.users_df[(st.session_state.users_df['email'] == email) & (st.session_state.users_df['password'] == hashed_password)]
        if not user.empty:
            if user.iloc[0]['approved']:
                st.session_state['authenticated'] = True
                st.session_state['current_user'] = user.iloc[0]['email']
                st.session_state['is_admin'] = user.iloc[0]['role'] == 'admin'
                st.success(f"Welcome {st.session_state['current_user']}!")
            else:
                st.warning("Your account is not approved by admin yet.")
        else:
            st.error("Invalid email or password")

# Function to approve users by admin
def admin_approve():
    st.title("Admin Approval")
    unapproved_users = st.session_state.users_df[~st.session_state.users_df['approved']]
    if not unapproved_users.empty:
        for idx, user in unapproved_users.iterrows():
            st.write(f"User: {user['email']}")
            if st.button(f"Approve {user['email']}", key=f"approve_{user['email']}"):
                st.session_state.users_df.loc[idx, 'approved'] = True
                save_users(st.session_state.users_df)
                st.success(f"User {user['email']} approved.")
    else:
        st.write("No users pending approval.")

# Function to change password
def change_password():
    st.title("Change Password")
    current_password = st.text_input("Current Password", type="password")
    new_password = st.text_input("New Password", type="password")
    confirm_new_password = st.text_input("Confirm New Password", type="password")

    if st.button("Change Password", key="change_password_button"):
        hashed_current_password = hashlib.sha256(current_password.encode()).hexdigest()
        if st.session_state.users_df[
            (st.session_state.users_df['email'] == st.session_state['current_user']) &
            (st.session_state.users_df['password'] == hashed_current_password)
        ].empty:
            st.error("Current password is incorrect.")
        elif new_password != confirm_new_password:
            st.error("New passwords do not match.")
        else:
            hashed_new_password = hashlib.sha256(new_password.encode()).hexdigest()
            st.session_state.users_df.loc[
                st.session_state.users_df['email'] == st.session_state['current_user'], 'password'
            ] = hashed_new_password
            save_users(st.session_state.users_df)
            st.success("Password changed successfully.")

# Main function
def main():
    if st.session_state['authenticated']:
        st.sidebar.title(f"Welcome, {st.session_state['current_user']}")
        st.sidebar.markdown("## Navigation")
        if st.session_state.is_admin:
            admin_dashboard()
        else:
            user_dashboard()

        st.sidebar.markdown("---")
        if st.sidebar.button("Change Password", key="show_change_password_button"):
            st.session_state['show_change_password'] = True

        if st.session_state['show_change_password']:
            change_password()
    else:
        menu = ["Login", "Register", "Admin Approval"]
        choice = st.sidebar.selectbox("Choose an action", menu)

        if choice == "Login":
            login()
        elif choice == "Register":
            register()
        elif choice == "Admin Approval":
            admin_approve()

def show_dashboard():
    st.sidebar.title("Dashboard")
    projects = {
        "Productivity Calendar": productivity_calendar,  # Use the function instead of file path
    }

    choice = st.sidebar.selectbox("Choose a project", list(projects.keys()), key="project_select")

    if choice:
        projects[choice]()  # Call the function directly

def show_admin_dashboard():
    st.sidebar.title("Dashboard")
    projects = {
        "Productivity Calendar": productivity_calendar,  # Use the function instead of file path
    }

    choice = st.sidebar.selectbox("Choose a project", list(projects.keys()), key="project_select")

    if choice:
        projects[choice]()  # Call the function directly

def admin_dashboard():
    st.sidebar.title("Admin Options")
    admin_options = st.sidebar.selectbox("Admin Options", ["User Dashboard","Approve Users", "View Logs", "Manage Settings"], key="admin_options")

    if admin_options == "User Dashboard":
        show_admin_dashboard()
    elif admin_options == "Approve Users":
        admin_approve()
    elif admin_options == "View Logs":
        st.write("Admin Logs Placeholder")
        # Add functionality to view logs
    elif admin_options == "Manage Settings":
        st.write("Manage Settings Placeholder")
        # Add functionality to manage settings

if __name__ == "__main__":
    main()
