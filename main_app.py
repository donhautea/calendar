import streamlit as st
import pandas as pd
import hashlib
from functions import (
    read_data,
    read_linked_data,
    process_pdfs,
    compute_volatility,
    compute_average,
    get_latest_date,
    load_users,
    save_users,
    ensure_default_admin
)
from read_portfolio import portfolio_performance  # Import the function
from equity_transactions import equity_transactions
from equity_update import equity_update_tool
from equity_portfolio_viewer import equity_portfolio_viewer
from equity_update import equity_update_tool

# Set Streamlit page configuration to wide layout
st.set_page_config(layout="wide")

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

# Function for admin approval of users
def admin_approve():
    if not st.session_state['admin_authenticated']:
        st.title("Admin Login")
        email = st.text_input("Enter admin email address")
        password = st.text_input("Enter admin password", type="password")
        if st.button("Login as Admin", key="admin_login_button"):
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            admin_row = st.session_state.users_df[
                (st.session_state.users_df['email'] == email) &
                (st.session_state.users_df['password'] == hashed_password) &
                (st.session_state.users_df['role'] == 'admin')
            ]

            if not admin_row.empty:
                st.success("Admin logged in successfully!")
                st.session_state['admin_authenticated'] = True
                st.experimental_rerun()  # Refresh the page to show the admin approval
            else:
                st.error("Invalid admin credentials.")
    else:
        st.title("Admin Approval")
        pending_users = st.session_state.users_df[st.session_state.users_df['approved'] == False]
        user_roles = {}
        if not pending_users.empty:
            for index, row in pending_users.iterrows():
                st.write(f"Email: {row['email']}")
                role = st.selectbox(f"Select role for {row['email']}", ["user", "admin"], key=f"role_{index}")
                user_roles[row['email']] = role
                st.session_state.users_df.at[index, 'role'] = role

            if st.button("Approve Selected Users", key="approve_users_button"):
                for index, row in pending_users.iterrows():
                    st.session_state.users_df.at[index, 'approved'] = True
                save_users(st.session_state.users_df)
                st.success("Selected users approved!")
                st.experimental_rerun()
        else:
            st.info("No users awaiting approval.")

# Function for user login
def login():
    st.title("Login")
    email = st.text_input("Enter your email address")
    password = st.text_input("Enter your password", type="password")

    if st.button("Login", key="login_button"):
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        user_row = st.session_state.users_df[
            (st.session_state.users_df['email'] == email) &
            (st.session_state.users_df['password'] == hashed_password)
        ]

        if not user_row.empty:
            if user_row['approved'].values[0]:
                st.success("Logged in successfully!")
                st.session_state['authenticated'] = True
                st.session_state['current_user'] = email
                st.session_state['is_admin'] = user_row['role'].values[0] == 'admin'
                st.experimental_rerun()  # Refresh the page to show the dashboard
            else:
                st.warning("Your account is pending approval by the admin. Please wait.")
        else:
            st.error("Invalid credentials.")

def change_password():
    st.title("Change Password")
    current_password = st.text_input("Enter your current password", type="password")
    new_password = st.text_input("Enter your new password", type="password")
    confirm_new_password = st.text_input("Confirm your new password", type="password")

    if st.button("Change Password", key="change_password_button"):
        hashed_current_password = hashlib.sha256(current_password.encode()).hexdigest()
        user_row = st.session_state.users_df[
            (st.session_state.users_df['email'] == st.session_state['current_user']) &
            (st.session_state.users_df['password'] == hashed_current_password)
        ]

        if not user_row.empty:
            if new_password == confirm_new_password:
                hashed_new_password = hashlib.sha256(new_password.encode()).hexdigest()
                st.session_state.users_df.loc[
                    st.session_state.users_df['email'] == st.session_state['current_user'], 'password'
                ] = hashed_new_password
                save_users(st.session_state.users_df)
                st.success("Password changed successfully!")
            else:
                st.error("New passwords do not match.")
        else:
            st.error("Current password is incorrect.")

def main():
    st.sidebar.title("Authentication App")

    if st.session_state['authenticated']:
        if st.session_state['is_admin']:
            admin_dashboard()
        else:
            show_dashboard()

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
        "Portfolio Performance": portfolio_performance,  # Use the function instead of file path
        "User Tool": portfolio_performance,
    }

    choice = st.sidebar.selectbox("Choose a project", list(projects.keys()), key="project_select")

    if choice:
        projects[choice]()  # Call the function directly

def show_admin_dashboard():
    st.sidebar.title("Dashboard")
    projects = {
        "Portfolio Performance": portfolio_performance,  # Use the function instead of file path
        "Equity Transaction Viewer": equity_transactions,
        "Equity Transaction Update Tool": equity_update_tool,
        "Equity Portfolio Viewer": equity_portfolio_viewer,
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
