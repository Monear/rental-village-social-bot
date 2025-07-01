# src/suggest_content.py
import os
import argparse
from dotenv import load_dotenv
from src.utils.general import read_file_content
from src.utils.gemini_helpers import generate_ideas_with_gemini, generate_image_with_gemini
from src.utils.notion_helpers import add_idea_to_notion, get_existing_notion_ideas
import notion_client
import json

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

    social_media_best_practices_path = os.path.join(script_dir, 'prompts', 'social_media_best_practices.md')
    social_media_best_practices = read_file_content(social_media_best_practices_path)
    if not social_media_best_practices:
        print("Warning: Social media best practices document not found. Proceeding without this context.")
        social_media_best_practices = ""

    # Load Machine Context Provider (MCP)
    mcp_path = os.path.join(script_dir, 'data', 'machine_context.json')
    try:
        with open(mcp_path, 'r') as f:
            machine_context = json.load(f)
    except FileNotFoundError:
        print(f"Warning: Machine context file not found at {mcp_path}. Proceeding without MCP.")
        machine_context = {}
    except json.JSONDecodeError:
        print(f"Warning: Could not decode JSON from {mcp_path}. Proceeding without MCP.")
        machine_context = {}

    notion = notion_client.Client(auth=NOTION_API_KEY)
    
    print("Fetching existing ideas from Notion...")
    existing_ideas = get_existing_notion_ideas(notion, NOTION_DATABASE_ID)
    print(f"Found {len(existing_ideas)} existing ideas.")

    ideas = generate_ideas_with_gemini(content_guidelines, args.num_ideas, args.input_text, existing_ideas, machine_context, social_media_best_practices)

    if not ideas:
        print("No ideas were generated. Exiting.")
        return

    print("\nStarting to add new content ideas to Notion...")
    for idea in ideas:
        add_idea_to_notion(notion, idea, generate_image_with_gemini, num_images=3)
    print("Finished adding ideas.")

if __name__ == "__main__":
    main()