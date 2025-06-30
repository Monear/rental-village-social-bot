# src/suggest_content.py
import os
import argparse
from dotenv import load_dotenv
from utils.general import read_file_content
from utils.gemini_helpers import generate_ideas_with_gemini, generate_image_with_gemini
from utils.notion_helpers import add_idea_to_notion, get_existing_notion_ideas
import notion_client

# Load environment variables
load_dotenv()

# --- Configuration ---
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def main():
    parser = argparse.ArgumentParser(description="Generate social media content ideas and add them to Notion.")
    parser.add_argument("--num-ideas", type=int, default=3, help="Number of content ideas to generate.")
    parser.add_argument("--input-text", type=str, help="Pasted text to use as inspiration for idea generation.")
    args = parser.parse_args()

    if not all([NOTION_API_KEY, NOTION_DATABASE_ID, GEMINI_API_KEY]):
        raise ValueError("Required API keys (NOTION, GEMINI) must be set in the .env file.")

    script_dir = os.path.dirname(__file__)
    guidelines_path = os.path.join(script_dir, 'prompts', 'content_generation_prompt.md')
    content_guidelines = read_file_content(guidelines_path)
    if not content_guidelines:
        return

    notion = notion_client.Client(auth=NOTION_API_KEY)
    
    print("Fetching existing ideas from Notion...")
    existing_ideas = get_existing_notion_ideas(notion, NOTION_DATABASE_ID)
    print(f"Found {len(existing_ideas)} existing ideas.")

    ideas = generate_ideas_with_gemini(content_guidelines, args.num_ideas, args.input_text, existing_ideas)

    if not ideas:
        print("No ideas were generated. Exiting.")
        return

    print("\nStarting to add new content ideas to Notion...")
    for idea in ideas:
        add_idea_to_notion(notion, idea, generate_image_with_gemini, num_images=3)
    print("Finished adding ideas.")

if __name__ == "__main__":
    main()