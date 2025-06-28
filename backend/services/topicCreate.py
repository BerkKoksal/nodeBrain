import os
import google.generativeai as genai
import json
from dotenv import load_dotenv

# Load API key from environment variable (recommended)
# If using python-dotenv, make sure load_dotenv() is called at the start of your app

load_dotenv()

# Configure the Gemini API
# The SDK will automatically pick up GOOGLE_API_KEY from environment variables
# Or you can pass it explicitly: genai.configure(api_key="YOUR_API_KEY_HERE")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def generate_learning_roadmap(learning_goal: str) -> list:
    """
    Generates a learning roadmap (list of topics) for a given goal using Gemini.
    """
    model = genai.GenerativeModel('gemini-2.0-flash') 
    prompt = f"""
    You are an expert educational curriculum designer. Your task is to break down a given learning goal into a structured, step-by-step roadmap of topics.
    The topics should progress from easiest to hardest, clearly indicating prerequisites.

    Provide the output as a JSON array of objects. The entire output MUST be a single, valid JSON array.
    Do not include any introductory or concluding text, explanations, or markdown fences (```json) outside of the JSON array itself.
    Start directly with `[` and end with `]`.

    Each object in the JSON array MUST contain all specified keys and valid values:
    - "id": A unique string identifier for the topic (e.g., "intro_python", "data_structures_1").
            Ensure that all generated `id`s are unique and that no topic is duplicated in the output array.
            Consolidate conceptually similar topics under a single, well-defined topic.
    - "title": The name of the topic.
    - "description": A brief, concise description of what the topic covers.
    - "difficulty": A string indicating the estimated difficulty (e.g., "beginner", "intermediate", "advanced").
    - "prerequisites": An array of "id" strings of topics that must be learned before this topic. If no prerequisites, provide an empty array [].
                      Ensure that any topic listed as a prerequisite appears earlier in the array than the topic that requires it.

    Learning Goal: "{learning_goal}"

    Example Output Structure (if the goal was "Learn Web Development"):
    [
      {{
        "id": "html_basics",
        "title": "HTML Basics",
        "description": "Understanding the fundamental structure of web pages with HTML5.",
        "difficulty": "beginner",
        "prerequisites": []
      }},
      {{
        "id": "css_fundamentals",
        "title": "CSS Fundamentals",
        "description": "Styling web pages with CSS, including selectors, properties, and layout.",
        "difficulty": "beginner",
        "prerequisites": ["html_basics"]
      }},
      {{
        "id": "js_intro",
        "title": "Introduction to JavaScript",
        "description": "Basic programming concepts and DOM manipulation using JavaScript.",
        "difficulty": "intermediate",
        "prerequisites": ["html_basics", "css_fundamentals"]
      }}
    ]

    Now, generate the roadmap for the learning goal: "{learning_goal}"
    """

    try:
        response = model.generate_content(prompt)
        # Access the text from the response
        raw_json_string = response.text.strip()

        # extract the pure JSON.
        if raw_json_string.startswith("```json"):
            raw_json_string = raw_json_string.replace("```json\n", "").replace("\n```", "")
        elif raw_json_string.startswith("```"):
             # Handle cases where it might just use triple backticks without 'json'
            raw_json_string = raw_json_string.replace("```\n", "").replace("\n```", "")

        # Attempt to parse the JSON
        topics = json.loads(raw_json_string)
        return topics

    except Exception as e:
        print(f"Error generating roadmap: {e}")
        # This is where you'd handle rate limits, invalid JSON, etc.
        # You might want to log the full response for debugging: print(response.candidates[0].text)
        return []

if __name__ == "__main__":
    goal = input("What do you want to learn? ")
    roadmap = generate_learning_roadmap(goal)

    if roadmap:
        print("\nGenerated Learning Roadmap:")
        for topic in roadmap:
            print(f"ID: {topic.get('id')}")
            print(f"Title: {topic.get('title')}")
            print(f"Description: {topic.get('description')}")
            print(f"Difficulty: {topic.get('difficulty')}")
            print(f"Prerequisites: {', '.join(topic.get('prerequisites', []))}")
            print("-" * 20)
    else:
        print("Could not generate a roadmap. Please try again or refine your input.")