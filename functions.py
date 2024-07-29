import re
import shutil
import pandas as pd
import numpy as np
import hashlib
from datetime import datetime
import os


# Function to get the latest date in the CSV file
def get_latest_date(file_path):
    df = pd.read_csv(file_path, index_col='Date', parse_dates=True)
    return df.index.max()

# Function to load users from a CSV file
def load_users():
    if os.path.exists('users.csv'):
        df = pd.read_csv('users.csv')
        if 'role' not in df.columns:
            df['role'] = 'user'  # Default role is 'user'
        return df
    else:
        return pd.DataFrame(columns=['email', 'password', 'approved', 'role'])

# Function to save users to a CSV file
def save_users(df):
    df.to_csv('users.csv', index=False)

# Ensure a default admin account exists
def ensure_default_admin(users_df):
    admin_email = 'admin'
    admin_password = 'fmgsss'
    hashed_password = hashlib.sha256(admin_password.encode()).hexdigest()
    admin_row = users_df[
        (users_df['email'] == admin_email) &
        (users_df['password'] == hashed_password) &
        (users_df['role'] == 'admin')
    ]
    if admin_row.empty:
        new_admin = pd.DataFrame({
            'email': [admin_email],
            'password': [hashed_password],
            'approved': [True],
            'role': ['admin']
        })
        users_df = pd.concat([users_df, new_admin], ignore_index=True)
        save_users(users_df)
    return users_df
