import json
from langchain.prompts import PromptTemplate
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI

def main():
    # Get user input
    goal_description = input("Enter your goal: ").strip()
    duration_weeks = input("Enter duration in weeks: ").strip()

    # Prepare LangChain prompt template
    prompt_template = """
You are a helpful assistant that converts a user's goal into a week-wise habit plan.

User Goal: {goal_description}
Duration (in weeks): {duration}

Generate a JSON object where each key is 'week_1', 'week_2', etc. up to the duration, and the value is a list of 2-3 simple habits for that week that help achieve the goal.

Output ONLY the JSON in the response, nothing else.
"""

    prompt = PromptTemplate(
        input_variables=["goal_description", "duration"],
        template=prompt_template
    )

    # Format prompt
    prompt_text = prompt.format(goal_description=goal_description, duration=duration_weeks)

    # Initialize Gemini model (make sure GOOGLE_APPLICATION_CREDENTIALS is set in your environment)
    llm = ChatGoogleGenerativeAI(model="models/gemini-1.5-flash", temperature=0.7)

    # Get response
    response = llm.predict(prompt_text)

    text = response.strip()

    # Remove code block markdown if present
    if text.startswith("```"):
        # Split by triple backticks and take the middle part
        parts = text.split("```")
        if len(parts) >= 3:
            text = parts[1].strip()

    # Parse JSON and handle errors
    try:
        habits = json.loads(text)
        print("\n✅ Weekly Habit Plan:")
        print(json.dumps(habits, indent=2))

        # Save to file
        with open("goal_plan.json", "w") as f:
            json.dump({
                "goal_description": goal_description,
                "duration_weeks": duration_weeks,
                "plan": habits
            }, f, indent=2)

        print("\n✅ Goal and plan saved to goal_plan.json")

    except Exception as e:
        print("❌ Failed to parse response as JSON:")
        print(text)
        print("\nError:", e)

if __name__ == "__main__":
    main()
