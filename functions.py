import pdfplumber
import re
import shutil
import pandas as pd
import numpy as np
import hashlib
from datetime import datetime
import os

# Function to read data from the uploaded file
def read_data(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file)
        return df
    except Exception as e:
        return None

# Function to read data from the linked path
def read_linked_data(path):
    try:
        df = pd.read_csv(path)
        return df
    except Exception as e:
        return None

# Function to process PDF files and extract data
def process_pdfs(directory):
    all_data = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".pdf"):
                full_path = os.path.join(root, file)
                data = extract_data_from_pdf(full_path)
                date_pattern = r"(\d{4}-\d{2}-\d{2})"
                match = re.search(date_pattern, file)
                if match:
                    extracted_date = datetime.strptime(match.group(1), "%Y-%m-%d")
                    for row in data:
                        row.append(extracted_date)
                all_data.extend(data)
    return pd.DataFrame(all_data, columns=["Tenor", "BVAL Rate Today", "Date"]).set_index("Date")

# Function to extract data from a PDF file
def extract_data_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        text = page.extract_text()
    rows = text.split("\n")[1:]
    return [row.split()[:2] for row in rows]

# Function to compute volatility
def compute_volatility(df, tenor, period):
    df_filtered = df[df['Tenor'] == tenor]
    df_filtered['Daily Returns'] = df_filtered['BVAL Rate Today'].pct_change()
    period_days = {"2Y": 504, "1.5Y": 378, "1Y": 252, "6M": 126, "3M": 63, "1M": 21, "1W": 5}
    days = period_days.get(period, 252)
    return df_filtered['Daily Returns'].tail(days).std() * (252 ** 0.5)

# Function to compute average
def compute_average(df, tenor, period):
    df_filtered = df[df['Tenor'] == tenor]
    period_days = {"2Y": 504, "1.5Y": 378, "1Y": 252, "6M": 126, "3M": 63, "1M": 21, "1W": 5}
    days = period_days.get(period, 252)
    return df_filtered['BVAL Rate Today'].tail(days).mean()

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
