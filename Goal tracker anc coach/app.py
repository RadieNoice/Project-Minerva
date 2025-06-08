import streamlit as st
from typing import Dict, List
from dotenv import load_dotenv
import os
import json
from langchain_together.chat_models import ChatTogether
from langchain.schema import HumanMessage

# Load API key from .env
load_dotenv()
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")


def extract_json(text: str) -> str:
    """Extract the JSON part from a larger text blob."""
    start = text.find('{')
    end = text.rfind('}')
    if start == -1 or end == -1:
        return ""
    return text[start:end + 1]


def generate_habit_plan(goal: str, weeks: int) -> Dict[str, List[str]]:
    """Use Together LLM to generate habit plan."""
    try:
        llm = ChatTogether(
            api_key=TOGETHER_API_KEY,
            model="meta-llama/Llama-3-8b-chat-hf"
        )

        prompt = f"""
I want to achieve the goal: "{goal}" in {weeks} weeks.
Provide a week-wise breakdown of 2-3 specific, actionable, and realistic tasks per week that I can follow.
Return the output strictly as valid JSON in this format:

{{
  "week_1": ["task 1", "task 2"],
  "week_2": ["task 3", "task 4"],
  ...
}}
"""

        response = llm.invoke([HumanMessage(content=prompt)])
        raw_json = extract_json(response.content)
        return json.loads(raw_json)

    except Exception as e:
        st.error(f"⚠️ Error: {e}")
        return {}


st.set_page_config(page_title="Goal Tracker Agent", layout="centered")
st.title("🎯 Goal Tracker & Weekly Habit Planner")

# Step 1: Input
with st.form("goal_input_form"):
    goal = st.text_input("Enter your goal:")
    weeks = st.number_input("Duration (in weeks):", min_value=1, step=1)
    submitted = st.form_submit_button("Generate Plan")

if submitted:
    with st.spinner("Generating habit plan..."):
        plan = generate_habit_plan(goal, weeks)

    if plan:
        st.session_state["plan"] = plan
        st.session_state["goal"] = goal
        st.session_state["weeks"] = weeks

# Step 2: Show Weekly Plan
if "plan" in st.session_state:
    st.subheader("📅 Weekly Habit Plan")

    for week, tasks in st.session_state["plan"].items():
        st.markdown(f"**{week.capitalize()}**")
        for task in tasks:
            st.markdown(f"- {task}")

    if "confirmed" not in st.session_state:
        if st.button("✅ Confirm and Add Task Timings"):
            st.session_state["confirmed"] = True

# Step 3: Ask for time per task
if "confirmed" in st.session_state:
    st.subheader("⏰ Assign Time to Each Task")

    timed_plan = {}
    with st.form("time_assignment_form"):
        for week, tasks in st.session_state["plan"].items():
            st.markdown(f"### {week.capitalize()}")
            timed_plan[week] = []
            for idx, task in enumerate(tasks):
                time_input = st.time_input(f"{task}", key=f"{week}_{idx}")
                timed_plan[week].append({"task": task, "time": time_input.strftime("%H:%M")})

        save_button = st.form_submit_button("💾 Save Plan with Times")

    if save_button:
        st.session_state["timed_plan"] = timed_plan

# Final Output
if "timed_plan" in st.session_state:
    st.subheader("✅ Final Structured Habit Plan with Times")
    for week, entries in st.session_state["timed_plan"].items():
        st.markdown(f"### {week.capitalize()}")
        for entry in entries:
            st.markdown(f"⏰ `{entry['time']}` – {entry['task']}")

    # Save to JSON
    if st.button("📂 Download Plan as JSON"):
        goal_slug = st.session_state["goal"].strip().lower().replace(" ", "_")
        filename = f"habit_plan_{goal_slug}.json"
        with open(filename, "w") as f:
            json.dump(st.session_state["timed_plan"], f, indent=2)
        st.success(f"Plan saved as `{filename}` in your project folder.")

import datetime
from calendar_utils import authenticate_google_calendar, create_events_from_plan

if "timed_plan" in st.session_state:
    if st.button("📅 Push to Google Calendar"):
        with st.spinner("Authenticating and creating events..."):
            try:
                calendar_service = authenticate_google_calendar()
                today = datetime.date.today()
                create_events_from_plan(calendar_service, st.session_state["timed_plan"], today)
                st.success("All tasks pushed to your Google Calendar 🎉")
            except Exception as e:
                st.error(f"Something went wrong: {e}")
