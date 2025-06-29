# src/suggest_content.py
import os
import argparse
import json
import random
from datetime import date, timedelta
import notion_client
import google.generativeai as genai
from pexelsapi.pexels import Pexels
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Configuration ---
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

# --- Helper Functions ---

def read_file_content(file_path):
    """Reads the content of a specified file."""
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return None

def search_images(query, num_images=5):
    """Searches for images using the Pexels API."""
    if not PEXELS_API_KEY:
        print("Warning: PEXELS_API_KEY is not set. Skipping image search.")
        return []
    try:
        pexel = Pexels(PEXELS_API_KEY)
        search_results = pexel.search_photos(query=query, per_page=num_images)
        return search_results.get('photos', [])
    except Exception as e:
        print(f"Error searching for images on Pexels: {e}")
        return []

def select_best_image_with_gemini(post_body, images):
    """Uses Gemini to select the most thematically appropriate image for a post."""
    if not images:
        return None

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

    image_options = "\n".join([f"- URL: {img['src']['original']}, Description: {img['alt']}" for img in images])

    prompt = f"""
    You are an expert art director. Your task is to choose the best image for a social media post.

    This is the post's content:
    ---
    {post_body}
    ---

    Here are the image options available:
    ---
    {image_options}
    ---

    Review the post and the image options carefully. Select the single best image that matches the tone, message, and subject matter of the post.
    Return only the URL of your chosen image, and nothing else.
    """
    print("Asking AI art director to select the best image...")
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error selecting image with Gemini: {e}")
        return None

def generate_ideas_with_gemini(guidelines, num_ideas, user_input=None):
    """Generates content ideas using the Gemini API."""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY must be set in the .env file.")

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"""
    You are a creative social media manager for a tool rental company.
    Your task is to generate {num_ideas} fresh, engaging content ideas.
    Adhere strictly to the following Content Guidelines:
    ---
    {guidelines}
    ---
    """
    if user_input:
        prompt += f"Base your suggestions on this user-provided text:\n---\n{user_input}\n---\n"

    prompt += """
    For each idea, provide a content pillar, a short catchy title (under 100 chars), the full post body, and 3-5 relevant keywords for an image search.
    Return your response as a valid JSON array of objects. Each object must have "pillar", "title", "body", and "keywords" keys.
    Example:
    [
        {
            "pillar": "Tool Spotlight",
            "title": "Mini-Excavator: Small But Mighty",
            "body": "Check out this 15-second video on the versatility of our new mini-excavator. Perfect for tight spaces and big jobs! #ToolRental #Excavator",
            "keywords": "excavator, construction, digging, small space"
        }
    ]
    """
    print("Generating content ideas with Gemini...")
    try:
        response = model.generate_content(prompt)
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned_response)
    except Exception as e:
        print(f"Error generating ideas with Gemini: {e}")
        print(f"Raw response from API: {response.text}")
        return []

def add_idea_to_notion(notion, idea):
    """Adds a single content idea, with an image, to the Notion database."""
    suggested_date = (date.today() + timedelta(days=random.randint(7, 14))).isoformat()
    
    # Find the best image for the post
    images = search_images(idea['keywords'])
    best_image_url = select_best_image_with_gemini(idea['body'], images)

    properties = {
        "Name": {"title": [{"text": {"content": idea['title']}}]},
        "Status": {"status": {"name": "AI Suggestion"}},
        "Content Pillar": {"select": {"name": idea['pillar']}},
        "Post Date": {"date": {"start": suggested_date}},
        "Copy": {"rich_text": [{"type": "text", "text": {"content": idea['body']}}]}
    }
    if best_image_url:
        properties["Creative"] = {"files": [{"name": best_image_url, "type": "external", "external": {"url": best_image_url}}]}

    try:
        notion.pages.create(parent={"database_id": NOTION_DATABASE_ID}, properties=properties)
        print(f"Successfully added idea: {idea['title']}")
        if best_image_url:
            print(f"  - with image: {best_image_url}")
    except Exception as e:
        print(f"Error adding idea to Notion: {e}")

def main():
    parser = argparse.ArgumentParser(description="Generate social media content ideas and add them to Notion.")
    parser.add_argument("--num-ideas", type=int, default=3, help="Number of content ideas to generate.")
    parser.add_argument("--input-text", type=str, help="Pasted text to use as inspiration for idea generation.")
    args = parser.parse_args()

    if not all([NOTION_API_KEY, NOTION_DATABASE_ID, GEMINI_API_KEY]):
        raise ValueError("Required API keys (NOTION, GEMINI) must be set in the .env file.")

    script_dir = os.path.dirname(__file__)
    guidelines_path = os.path.join(script_dir, '..', 'strategy_documents', 'content_guidelines.md')
    content_guidelines = read_file_content(guidelines_path)
    if not content_guidelines:
        return

    notion = notion_client.Client(auth=NOTION_API_KEY)
    ideas = generate_ideas_with_gemini(content_guidelines, args.num_ideas, args.input_text)

    if not ideas:
        print("No ideas were generated. Exiting.")
        return

    print("\nStarting to add new content ideas to Notion...")
    for idea in ideas:
        add_idea_to_notion(notion, idea)
    print("Finished adding ideas.")

if __name__ == "__main__":
    main()
