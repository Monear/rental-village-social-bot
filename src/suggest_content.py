# src/suggest_content.py
import os
import sys
import argparse
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.general import read_file_content
from src.utils.gemini_helpers import generate_ideas_with_gemini, generate_image_with_gemini
from src.utils.notion_helpers import add_idea_to_notion, get_existing_notion_ideas
from src.utils.sanity_helpers import save_social_content_to_sanity
import notion_client
import json
import logging
from sanity.client import Client

# Load environment variables
load_dotenv(dotenv_path='/Users/tyler/Documents/rental_village/social_media/.env', override=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuration ---
NOTION_API_KEY = os.getenv("NOTION_TOKEN")
NOTION_DATABASE_ID = os.getenv("DATABASE_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Sanity client configuration
SANITY_PROJECT_ID = os.environ.get("SANITY_PROJECT_ID", "2pxuaj9k")
SANITY_DATASET = os.environ.get("SANITY_DATASET", "production")
SANITY_API_TOKEN = os.environ.get("SANITY_API_TOKEN") # Ensure this is set in your environment variables

sanity_client = Client(
    project_id=SANITY_PROJECT_ID,
    dataset=SANITY_DATASET,
    token=SANITY_API_TOKEN,
    use_cdn=True, # Use CDN for faster reads
    logger=logger
)

def main():
    parser = argparse.ArgumentParser(description="Generate social media content ideas and add them to Notion.")
    parser.add_argument("--num-ideas", type=int, default=3, help="Number of content ideas to generate.")
    parser.add_argument("--input-text", type=str, help="Pasted text to use as inspiration for idea generation.")
    args = parser.parse_args()

    if not all([NOTION_API_KEY, NOTION_DATABASE_ID, GEMINI_API_KEY, SANITY_API_TOKEN]):
        raise ValueError("Required API keys (NOTION, GEMINI, SANITY) must be set in the .env file.")

    # Fetch content guidelines from Sanity
    try:
        query_result = sanity_client.query(
            groq='*[_type == "contentPrompt" && title == "Content Generation Prompt"][0]'
        )
        content_guidelines_doc = query_result.get('result')
        content_guidelines = content_guidelines_doc.get('content') if content_guidelines_doc else ""
        if not content_guidelines:
            print("Error: Content generation prompt not found in Sanity.")
            return
    except Exception as e:
        print(f"Error fetching content guidelines from Sanity: {e}")
        return

    # Fetch social media best practices from Sanity
    try:
        query_result = sanity_client.query(
            groq='*[_type == "contentPrompt" && title == "Social Media Best Practices"][0]'
        )
        social_media_best_practices_doc = query_result.get('result')
        social_media_best_practices = social_media_best_practices_doc.get('content') if social_media_best_practices_doc else ""
        if not social_media_best_practices:
            print("Warning: Social media best practices document not found in Sanity. Proceeding without this context.")
            social_media_best_practices = ""
    except Exception as e:
        print(f"Warning: Error fetching social media best practices from Sanity: {e}. Proceeding without this context.")
        social_media_best_practices = ""

    # Fetch business context from Sanity
    try:
        query_result = sanity_client.query(
            groq='*[_type == "businessContext"][0]'
        )
        business_context = query_result.get('result')
        if not business_context:
            print("Warning: Business context not found in Sanity. Proceeding without business context.")
            business_context = {}
    except Exception as e:
        print(f"Warning: Error fetching business context from Sanity: {e}. Proceeding without business context.")
        business_context = {}

    notion = notion_client.Client(auth=NOTION_API_KEY)
    
    print("Fetching existing ideas from Notion...")
    existing_ideas = get_existing_notion_ideas(notion, NOTION_DATABASE_ID)
    print(f"Found {len(existing_ideas)} existing ideas.")

    ideas = generate_ideas_with_gemini(content_guidelines, args.num_ideas, args.input_text, existing_ideas, business_context, social_media_best_practices)

    if not ideas:
        print("No ideas were generated. Exiting.")
        return

    print("\nStarting to process new content ideas...")
    for idea in ideas:
        sanity_doc_id = save_social_content_to_sanity(idea)
        if sanity_doc_id:
            print(f"Idea saved to Sanity with ID: {sanity_doc_id}")
            # Optionally, you could pass the Sanity doc ID to Notion for linking
            # For now, we proceed with Notion sync as before
            add_idea_to_notion(notion, idea, generate_image_with_gemini, num_images=3)
        else:
            print(f"Failed to save idea to Sanity. Skipping Notion sync for this idea: {idea.get('title', 'Unknown Title')}")
    print("Finished processing ideas.")

if __name__ == "__main__":
    main()