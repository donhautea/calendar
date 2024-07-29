import streamlit as st
import json
from datetime import datetime

def add_css():
    st.markdown(
        """
        <style>
        .column {
            border: 1px solid #d3d3d3;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .notes-section {
            border-top: 1px solid #d3d3d3;
            padding-top: 10px;
            margin-top: 20px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def productivity_calendar():
    # Title of the app
    st.title("Productivity Dashboard")

    add_css()

    # Initialize session state variables if they don't exist
    if 'tasks' not in st.session_state:
        st.session_state.tasks = []
    if 'notes' not in st.session_state:
        st.session_state.notes = []

    # Create three columns
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="notes-section">', unsafe_allow_html=True)
        # Sidebar with calendar
        st.sidebar.header("Calendar")
        selected_date = st.sidebar.date_input("Select a date", datetime.now())

        # Notes section
        st.header("Notes")
        note_tag = st.text_input("Tag your note", key="note_tag_input")
        note_content = st.text_area("Write your notes here", key="note_content_input")

        if st.button("Add Note"):
            if note_tag and note_content:
                st.session_state.notes.append({"date": str(selected_date), "tag": note_tag, "content": note_content})
                st.experimental_rerun()  # Clear the input fields by rerunning the script
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="notes-section">', unsafe_allow_html=True)
        # Display tasks
        st.header("Tasks")
        for i, task in enumerate(st.session_state.tasks):
            cols = st.columns([0.02, 0.5, 0.15])
            done = cols[0].checkbox("", value=task['done'], key=f"checkbox_{i}")
            if done:
                st.session_state.tasks[i]['done'] = True
            else:
                st.session_state.tasks[i]['done'] = False
            cols[1].write(task['task'])
            if cols[2].button("Remove", key=f"remove_{i}"):
                st.session_state.tasks.pop(i)
                st.experimental_rerun()

        # Save and load the notes and tasks
        if st.button("Save Data"):
            data = {
                "date": str(selected_date),
                "notes": st.session_state.notes,
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
                st.session_state.tasks = data["tasks"]
                st.session_state.notes = data["notes"]
                st.experimental_rerun()
            except FileNotFoundError:
                st.error("No saved data found.")
            except Exception as e:
                st.error(f"An error occurred: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="notes-section">', unsafe_allow_html=True)
        st.sidebar.subheader("Selected Date:")
        st.sidebar.write(selected_date)

        # Display tasks
        st.subheader("Your To-Do List:")
        for task in st.session_state.tasks:
            st.write(f"{'[x]' if task['done'] else '[ ]'} {task['task']}")
        st.markdown('</div>', unsafe_allow_html=True)

    # Display notes
    st.markdown('<div class="notes-section">', unsafe_allow_html=True)
    st.subheader("Your Notes:")
    for i, note in enumerate(st.session_state.notes):
        if note['date'] == str(selected_date):
            st.write(f"**Tag:** {note['tag']}\n**Content:** {note['content']}")
            if st.button("Delete Note", key=f"delete_note_{i}"):
                st.session_state.notes.pop(i)
                st.experimental_rerun()
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    productivity_calendar()
