import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Set up the page configuration
st.set_page_config(page_title="Productivity Dashboard", layout="wide")

# Title of the app
st.title("Productivity Dashboard")

# Sidebar with calendar
st.sidebar.header("Calendar")
selected_date = st.sidebar.date_input("Select a date", datetime.now())

# Notes section
st.header("Notes")
notes = st.text_area("Write your notes here")

# To-Do List section
st.header("To-Do List")

if 'tasks' not in st.session_state:
    st.session_state.tasks = []

new_task = st.text_input("New Task")
if st.button("Add Task"):
    if new_task:
        st.session_state.tasks.append({"task": new_task, "done": False})

# Display tasks
for i, task in enumerate(st.session_state.tasks):
    cols = st.columns([0.05, 0.8, 0.15])
    done = cols[0].checkbox("", value=task['done'], key=i)
    if done:
        st.session_state.tasks[i]['done'] = True
    else:
        st.session_state.tasks[i]['done'] = False
    cols[1].write(task['task'])
    if cols[2].button("Remove", key=f"remove-{i}"):
        st.session_state.tasks.pop(i)
        st.experimental_rerun()

# Save and load the notes and tasks
if st.button("Save Data"):
    data = {
        "date": selected_date,
        "notes": notes,
        "tasks": st.session_state.tasks,
    }
    with open("productivity_data.json", "w") as f:
        json.dump(data, f)

if st.button("Load Data"):
    try:
        with open("productivity_data.json", "r") as f:
            data = json.load(f)
        selected_date = data["date"]
        notes = data["notes"]
        st.session_state.tasks = data["tasks"]
    except FileNotFoundError:
        st.error("No saved data found.")

st.sidebar.subheader("Selected Date:")
st.sidebar.write(selected_date)

st.subheader("Your Notes:")
st.write(notes)

# Display tasks
st.subheader("Your To-Do List:")
for i, task in enumerate(st.session_state.tasks):
    st.write(f"{'[x]' if task['done'] else '[ ]'} {task['task']}")
