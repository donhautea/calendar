import streamlit as st
import json
from datetime import datetime

def productivity_calendar():
    # Title of the app
    st.title("Productivity Dashboard")

    # Sidebar with calendar
    st.sidebar.header("Calendar")
    selected_date = st.sidebar.date_input("Select a date", datetime.now())

    # Notes section
    st.header("Notes")
    notes = st.text_area("Write your notes here", key="notes")

    # To-Do List section
    st.header("To-Do List")

    if 'tasks' not in st.session_state:
        st.session_state.tasks = []

    new_task = st.text_input("New Task", key="new_task")
    if st.button("Add Task"):
        if new_task:
            st.session_state.tasks.append({"task": new_task, "done": False})
            st.session_state.new_task = ""  # Clear input after adding

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
            "date": str(selected_date),
            "notes": notes,
            "tasks": st.session_state.tasks,
        }
        with open("productivity_data.json", "w") as f:
            json.dump(data, f)
        st.success("Data saved successfully!")

    if st.button("Load Data"):
        try:
            with open("productivity_data.json", "r") as f:
                data = json.load(f)
            selected_date = datetime.strptime(data["date"], "%Y-%m-%d")
            st.session_state.notes = data["notes"]
            st.session_state.tasks = data["tasks"]
            st.experimental_rerun()
        except FileNotFoundError:
            st.error("No saved data found.")
        except Exception as e:
            st.error(f"An error occurred: {e}")

    st.sidebar.subheader("Selected Date:")
    st.sidebar.write(selected_date)

    st.subheader("Your Notes:")
    st.write(notes)

    # Display tasks
    st.subheader("Your To-Do List:")
    for i, task in enumerate(st.session_state.tasks):
        st.write(f"{'[x]' if task['done'] else '[ ]'} {task['task']}")

if __name__ == "__main__":
    productivity_calendar()
