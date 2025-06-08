import os
import json
from typing import Dict, List
from dotenv import load_dotenv
from langchain_together import ChatTogether
from langchain.schema import HumanMessage

def load_api_key() -> str:
    """Load and validate the Together API key."""
    load_dotenv()  # Load environment variables from .env file
    api_key = os.getenv("TOGETHER_API_KEY")
    if not api_key:
        raise ValueError(
            "Set your Together.ai API key in TOGETHER_API_KEY env variable"
        )
    return api_key

def extract_json(text: str) -> str:
    start = text.find('{')
    end = text.rfind('}')
    if start == -1 or end == -1:
        return ""
    return text[start:end+1]

def get_habit_plan(goal: str, weeks: int) -> Dict[str, List[str]]:
    """
    Generate a week-wise habit plan based on the goal and duration.

    Args:
        goal (str): The goal the user wants to achieve.
        weeks (int): Duration in weeks.

    Returns:
        Dict[str, List[str]]: A structured plan with weekly tasks.
    """
    try:
        api_key = load_api_key()

        # Initialize Together LLM with your API key
        llm = ChatTogether(
            api_key=api_key,
            model="meta-llama/Llama-3-8b-chat-hf"  # or other model you prefer
        )

        prompt = f"""
I want to achieve the goal: "{goal}" in {weeks} weeks.
Provide a week-wise breakdown of 2-3 specific, actionable, and realistic tasks per week that I can follow.
Return ONLY the JSON object and nothing else, in this format:

{{
  "week_1": ["task 1", "task 2"],
  "week_2": ["task 3", "task 4"],
  ...
}}
"""

        response = llm([HumanMessage(content=prompt)])

        json_str = extract_json(response.content)

        if not json_str:
            print("❌ Could not find JSON in the response.")
            return {}

        # Attempt to parse the extracted JSON
        try:
            plan = json.loads(json_str)
            return plan
        except json.JSONDecodeError:
            print("❌ Failed to parse extracted JSON:")
            print(json_str)
            return {}

    except Exception as e:
        print(f"⚠️ Error generating habit plan: {e}")
        return {}

def main() -> None:
    print("=== 🎯 Habit Plan Generator ===")
    goal = input("Enter your goal: ").strip()
    
    try:
        weeks = int(input("Enter duration in weeks: "))
        if weeks <= 0:
            raise ValueError("Duration must be a positive integer.")
    except ValueError as ve:
        print(f"Invalid input: {ve}")
        return

    habit_plan = get_habit_plan(goal, weeks)

    if habit_plan:
        print("\n📅 Generated Habit Plan:")
        for week, tasks in habit_plan.items():
            print(f"{week}:")
            for task in tasks:
                print(f"  - {task}")
    else:
        print("No valid habit plan was generated. Please try again.")

if __name__ == "__main__":
    main()
