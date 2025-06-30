# src/suggest_content.py
import os
import argparse
import json
import random
from datetime import date, timedelta
import notion_client
import google.generativeai as genai
from pyunsplash import PyUnsplash
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Configuration ---
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")

# --- Helper Functions ---

def read_file_content(file_path):
    """Reads the content of a specified file."""
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return None

def get_search_queries_with_gemini(post_body):
    """Uses a specialized AI prompt to generate effective search queries."""
    print("Asking AI Search Expert for the best queries...")
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    You are an expert at finding compelling images on stock photo sites like Unsplash.
    Based on the following social media post, generate 3-5 highly descriptive, effective search queries to find the perfect photo.
    Focus on action, results, and professional-looking images. Avoid generic terms.

    POST:
    ---
    {post_body}
    ---

    Return your response as a JSON array of strings.
    Example:
    ["professional deck power washing", "clean wood patio before and after", "outdoor deck restoration"]
    """
    try:
        response = model.generate_content(prompt)
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned_response)
    except Exception as e:
        print(f"Error generating search queries with Gemini: {e}")
        return []

def search_images_on_unsplash(queries, num_per_query=2):
    """Searches for images on Unsplash using a list of queries and consolidates the results."""
    if not UNSPLASH_ACCESS_KEY:
        print("Warning: UNSPLASH_ACCESS_KEY is not set. Skipping image search.")
        return []
    
    pu = PyUnsplash(api_key=UNSPLASH_ACCESS_KEY)
    all_image_urls = set() # Use a set to avoid duplicate images

    for query in queries:
        try:
            print(f"Searching Unsplash for: '{query}'")
            photos = pu.photos(type_='search', per_page=num_per_query, query=query)
            for photo in photos.entries:
                all_image_urls.add(photo.link_download)
        except Exception as e:
            print(f"Error searching Unsplash for '{query}': {e}")
            continue
            
    return list(all_image_urls)

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
    For each idea, provide a content pillar, a short catchy title (under 100 chars), and the full post body.
    Return your response as a valid JSON array of objects. Each object must have "pillar", "title", and "body" keys.
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
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned_response)
    except Exception as e:
        print(f"Error generating ideas with Gemini: {e}")
        print(f"Raw response from API: {response.text}")
        return []

def add_idea_to_notion(notion, idea):
    """Adds a single content idea, with image suggestions, to the Notion database."""
    suggested_date = (date.today() + timedelta(days=random.randint(7, 14))).isoformat()
    
    # Use the AI Search Expert to get better queries
    search_queries = get_search_queries_with_gemini(idea['body'])
    
    # Get a consolidated list of image URLs
    image_urls = search_images_on_unsplash(search_queries)
    
    properties = {
        "Name": {"title": [{"text": {"content": idea['title']}}]}
        "Status": {"status": {"name": "AI Suggestion"}},
        "Content Pillar": {"select": {"name": idea['pillar']}},
        "Post Date": {"date": {"start": suggested_date}},
        "Copy": {"rich_text": [{"type": "text", "text": {"content": idea['body']}}]}
    }

    if image_urls:
        image_links = "\n".join(image_urls)
        properties["Suggested Images"] = {"rich_text": [{"type": "text", "text": {"content": image_links}}]}
        print(f"Found {len(image_urls)} image suggestions for '{idea['title']}'.")

    try:
        notion.pages.create(parent={"database_id": NOTION_DATABASE_ID}, properties=properties)
        print(f"Successfully added idea: {idea['title']}")
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
