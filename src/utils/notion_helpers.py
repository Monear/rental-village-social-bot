# utils/notion_helpers.py
"""Helpers for Notion API interactions."""
import os
from pathlib import Path
import requests
from datetime import date, timedelta
import random
from dotenv import load_dotenv
from src.utils.general import read_file_content

load_dotenv()
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

def upload_image_to_notion(page_id, image_path, property_name="Creative"):
    """
    Uploads an image file to a Notion database page's files property using Notion's direct upload.
    """
    try:
        file_path = Path(image_path)
        file_name = file_path.name
        content_type_map = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.svg': 'image/svg+xml'
        }
        content_type = content_type_map.get(file_path.suffix.lower(), 'image/png')
        headers = {
            "Authorization": f"Bearer {NOTION_API_KEY}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
        initiate_payload = {
            "filename": file_name,
            "content_type": content_type
        }
        initiate_response = requests.post(
            "https://api.notion.com/v1/file_uploads", 
            headers=headers, 
            json=initiate_payload
        )
        initiate_response.raise_for_status()
        initiate_data = initiate_response.json()
        file_upload_id = initiate_data['id']
        with open(image_path, 'rb') as f:
            files = {
                "file": (file_name, f, content_type)
            }
            upload_headers = {
                "Authorization": f"Bearer {NOTION_API_KEY}",
                "Notion-Version": "2022-06-28"
            }
            upload_response = requests.post(
                f"https://api.notion.com/v1/file_uploads/{file_upload_id}/send",
                headers=upload_headers,
                files=files
            )
            upload_response.raise_for_status()
        upload_data = upload_response.json()
        page_response = requests.get(
            f"https://api.notion.com/v1/pages/{page_id}",
            headers=headers
        )
        page_response.raise_for_status()
        page_data = page_response.json()
        existing_files = []
        if property_name in page_data.get('properties', {}):
            existing_files = page_data['properties'][property_name].get('files', [])
        new_file = {
            "type": "file_upload",
            "file_upload": {
                "id": file_upload_id
            },
            "name": file_name
        }
        updated_files = existing_files + [new_file]
        update_payload = {
            "properties": {
                property_name: {
                    "type": "files",
                    "files": updated_files
                }
            }
        }
        update_response = requests.patch(
            f"https://api.notion.com/v1/pages/{page_id}",
            headers=headers,
            json=update_payload
        )
        update_response.raise_for_status()
        return True
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")
        return False
    except Exception as e:
        print(f"Error uploading file: {e}")
        return False

def get_existing_notion_ideas(notion, database_id):
    """Fetches existing content ideas (titles and copies) from the Notion database."""
    existing_ideas = []
    try:
        response = notion.databases.query(
            database_id=database_id,
            filter={
                "or": [
                    {"property": "Name", "title": {"is_not_empty": True}},
                    {"property": "Copy", "rich_text": {"is_not_empty": True}}
                ]
            }
        )
        for page in response["results"]:
            title = ""
            if "Name" in page["properties"] and page["properties"]["Name"]["type"] == "title":
                title_parts = page["properties"]["Name"]["title"]
                if title_parts:
                    title = title_parts[0]["plain_text"]

            copy = ""
            if "Copy" in page["properties"] and page["properties"]["Copy"]["type"] == "rich_text":
                copy_parts = page["properties"]["Copy"]["rich_text"]
                if copy_parts:
                    copy = copy_parts[0]["plain_text"]
            
            if title or copy:
                existing_ideas.append({"title": title, "copy": copy})
    except Exception as e:
        print(f"Error fetching existing Notion ideas: {e}")
    return existing_ideas

def add_idea_to_notion(notion, idea, generate_image_with_gemini, num_images=3):
    """Adds a single content idea, with up to n AI-generated images, to the Notion database."""
    suggested_date = (date.today() + timedelta(days=random.randint(7, 14))).isoformat()
    properties = {
        "Name": {"title": [{"text": {"content": idea['title']}}]},
        "Status": {"status": {"name": "AI Suggestion"}},
        "Content Pillar": {"select": {"name": idea['pillar']}},
        "Post Date": {"date": {"start": suggested_date}},
        "Copy": {"rich_text": [{"type": "text", "text": {"content": idea['body']}}]}
    }
    try:
        page_response = notion.pages.create(parent={"database_id": NOTION_DATABASE_ID}, properties=properties)
        page_id = page_response['id']
        # Read image generation instructions
        script_dir = os.path.dirname(__file__)
        image_instructions_path = os.path.join(script_dir, '..', 'prompts', 'image_generation_instructions.md')
        image_instructions = read_file_content(image_instructions_path)
        title_context = idea.get('title', '')
        body_context = idea.get('body', '')
        keywords_context = idea.get('keywords', '')
        base_image_prompt_parts = []
        if title_context: base_image_prompt_parts.append(f"Title: {title_context}")
        if body_context: base_image_prompt_parts.append(f"Description: {body_context}")
        if keywords_context: base_image_prompt_parts.append(f"Keywords: {keywords_context}")
        base_image_prompt = ". ".join(base_image_prompt_parts)
        image_prompt = f"{image_instructions}\n\n{base_image_prompt}" if image_instructions else base_image_prompt
        image_filename_base = idea['title'].replace(' ', '_').replace('/', '_')[:50]
        script_dir = os.path.dirname(__file__)
        images_dir = os.path.join(script_dir, '..', 'generated_images')
        os.makedirs(images_dir, exist_ok=True)
        output_path = os.path.join(images_dir, image_filename_base + ".png")
        image_paths = generate_image_with_gemini(image_prompt, output_path, num_images=num_images)
        if image_paths:
            for img_path in image_paths:
                success = upload_image_to_notion(page_id, img_path)
                if not success:
                    print(f"❌ Failed to upload image {img_path} to Notion for '{idea['title']}'")
        else:
            print(f"❌ Failed to generate images for '{idea['title']}'")
    except Exception as e:
        print(f"Error adding idea to Notion: {e}")
