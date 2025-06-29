# src/suggest_content.py
import os
import argparse
import json
import random
from datetime import date, timedelta
import notion_client
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- Helper Functions ---

def read_file_content(file_path):
    """Reads the content of a specified file."""
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return None

def generate_ideas_with_gemini(guidelines, num_ideas=3, user_input=None):
    """
    Generates content ideas using the Gemini API based on guidelines and optional user input.
    """
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY must be set in the .env file.")

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"""
    You are a creative social media manager for a tool rental company.
    Your task is to generate {num_ideas} fresh, engaging content ideas.

    Please adhere strictly to the following Content Guidelines:
    ---
    {guidelines}
    ---
    """

    if user_input:
        prompt += f"""
        A user has provided the following text for inspiration. Please base your suggestions on this input:
        ---
        {user_input}
        ---
        """

    prompt += """
    For each idea, provide a content pillar, a short, catchy title (under 100 characters), and the full post body.
    Return your response as a valid JSON array of objects, where each object has a "pillar", "title", and "body" key.
    Example:
    [
        {
            "pillar": "Tool Spotlight",
            "title": "Mini-Excavator: Small But Mighty",
            "body": "Check out this 15-second video on the versatility of our new mini-excavator. Perfect for tight spaces and big jobs! #ToolRental #Excavator"
        }
    ]
    """

    print("Generating content ideas with Gemini...")
    try:
        response = model.generate_content(prompt)
        # The response might be in a markdown block, so we need to clean it
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "").strip()
        ideas = json.loads(cleaned_response)
        return ideas
    except Exception as e:
        print(f"Error generating ideas with Gemini: {e}")
        print(f"Raw response from API: {response.text}")
        return []


def add_idea_to_notion(notion, idea_content):
    """
    Adds a single content idea to the Notion database.
    """
    suggested_date = (date.today() + timedelta(days=random.randint(7, 14))).isoformat()

    try:
        notion.pages.create(
            parent={"database_id": NOTION_DATABASE_ID},
            properties={
                "Name": {"title": [{"text": {"content": idea_content['title']}}]},
                "Status": {"status": {"name": "AI Suggestion"}},
                "Content Pillar": {"select": {"name": idea_content['pillar']}},
                "Post Date": {"date": {"start": suggested_date}},
            },
            children=[
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": idea_content['body']}}]
                    }
                }
            ]
        )
        print(f"Successfully added idea: {idea_content['title']}")
    except Exception as e:
        print(f"Error adding idea to Notion: {e}")

def main():
    """
    Main function to generate ideas and push them to Notion.
    """
    parser = argparse.ArgumentParser(description="Generate social media content ideas and add them to Notion.")
    parser.add_argument("--input-text", type=str, help="Pasted text to use as inspiration for idea generation.")
    args = parser.parse_args()

    if not NOTION_API_KEY or not NOTION_DATABASE_ID:
        raise ValueError("NOTION_API_KEY and NOTION_DATABASE_ID must be set in the .env file.")

    # Find the guidelines file relative to the script location
    script_dir = os.path.dirname(__file__)
    guidelines_path = os.path.join(script_dir, '..', 'strategy_documents', 'content_guidelines.md')
    content_guidelines = read_file_content(guidelines_path)

    if not content_guidelines:
        print("Could not proceed without content guidelines.")
        return

    notion = notion_client.Client(auth=NOTION_API_KEY)
    ideas_to_generate = generate_ideas_with_gemini(content_guidelines, user_input=args.input_text)

    if not ideas_to_generate:
        print("No ideas were generated. Exiting.")
        return

    print("\nStarting to add new content ideas to Notion...")
    for idea in ideas_to_generate:
        add_idea_to_notion(notion, idea)
    print("Finished adding ideas.")

if __name__ == "__main__":
    main()