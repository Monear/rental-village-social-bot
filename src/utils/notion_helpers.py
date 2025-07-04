# utils/notion_helpers.py
"""Helpers for Notion API interactions."""
import os
from pathlib import Path
import requests
from datetime import date, timedelta
import random
import time
from dotenv import load_dotenv
from src.utils.general import read_file_content

load_dotenv(override=True)
NOTION_API_KEY = os.getenv("NOTION_TOKEN")
NOTION_DATABASE_ID = os.getenv("DATABASE_ID")

def upload_image_to_notion(page_id, image_path, property_name="Creative"):
    """
    Uploads an image file to a Notion database page's files property using Notion's direct upload.
    Includes retry logic for 524 timeout errors.
    """
    max_retries = 3
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
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
                json=initiate_payload,
                timeout=30  # Add timeout
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
                    files=files,
                    timeout=120  # Longer timeout for file upload
                )
                upload_response.raise_for_status()
                
            upload_data = upload_response.json()
            page_response = requests.get(
                f"https://api.notion.com/v1/pages/{page_id}",
                headers=headers,
                timeout=30
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
                json=update_payload,
                timeout=30
            )
            update_response.raise_for_status()
            return True
            
        except requests.exceptions.HTTPError as e:
            if e.response and e.response.status_code == 524:
                print(f"❌ Attempt {attempt + 1} failed with 524 timeout. Retrying in {retry_delay} seconds...")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue
            print(f"HTTP Error: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response: {e.response.text}")
            return False
        except Exception as e:
            print(f"Error uploading file: {e}")
            return False
    
    print(f"❌ Failed to upload after {max_retries} attempts")
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
    """Adds a single content idea to the Notion database, using enhanced images if available."""
    suggested_date = (date.today() + timedelta(days=random.randint(7, 14))).isoformat()
    properties = {
        "Name": {"title": [{"text": {"content": idea['title']}}]},
        "Status": {"status": {"name": "Suggestion"}},
        "Content Pillar": {"select": {"name": idea['pillar']}},
        "Post Date": {"date": {"start": suggested_date}},
        "Copy": {"rich_text": [{"type": "text", "text": {"content": idea['body']}}]}
    }
    try:
        page_response = notion.pages.create(parent={"database_id": NOTION_DATABASE_ID}, properties=properties)
        page_id = page_response['id']
        
        # Check if enhanced images are already available (preferred method)
        enhanced_images = idea.get('enhanced_images', [])
        if enhanced_images:
            print(f"✅ Using {len(enhanced_images)} enhanced images (text suppression applied)")
            # Process enhanced images and upload to Notion
            for i, enhanced_image in enumerate(enhanced_images):
                try:
                    # Handle different image formats from enhanced generation
                    if enhanced_image.get('image_data'):
                        # Enhanced image with binary data
                        image_filename = f"{idea['title'].replace(' ', '_').replace('/', '_')[:50]}_enhanced_{i+1}.png"
                        script_dir = os.path.dirname(__file__)
                        images_dir = os.path.join(script_dir, '..', 'generated_images')
                        os.makedirs(images_dir, exist_ok=True)
                        image_path = os.path.join(images_dir, image_filename)
                        
                        # Save enhanced image data to file
                        with open(image_path, 'wb') as f:
                            f.write(enhanced_image['image_data'])
                        
                        success = upload_image_to_notion(page_id, image_path)
                        if not success:
                            print(f"❌ Failed to upload enhanced image {i+1} to Notion for '{idea['title']}'")
                    
                    elif enhanced_image.get('url'):
                        # Enhanced image with URL (fallback to original)
                        print(f"⚠️  Enhanced image {i+1} is URL-based, skipping upload")
                        
                except Exception as e:
                    print(f"❌ Error processing enhanced image {i+1}: {e}")
        
        else:
            # Fallback to legacy image generation (with text suppression applied)
            print(f"⚠️  No enhanced images found, falling back to legacy generation with text suppression")
            
            # Load text suppression settings from Sanity
            from sanity import Client
            import logging
            
            # Initialize Sanity client
            SANITY_PROJECT_ID = os.environ.get("SANITY_PROJECT_ID", "2pxuaj9k")
            SANITY_DATASET = os.environ.get("SANITY_DATASET", "production")
            SANITY_API_TOKEN = os.environ.get("SANITY_API_TOKEN")
            
            sanity_client = Client(
                project_id=SANITY_PROJECT_ID,
                dataset=SANITY_DATASET,
                token=SANITY_API_TOKEN,
                use_cdn=True,
                logger=logging.getLogger(__name__)
            )
            
            try:
                # Get image generation settings with text suppression
                query_result = sanity_client.query(
                    '*[_type == "imageGenerationSettings" && active == true][0]'
                )
                image_settings = query_result.get('result', {})
                text_suppression = image_settings.get('textSuppressionSettings', {})
                
                # Build text suppression prompt
                base_prompt = "Generate a professional, high-quality equipment rental image."
                suppression_prompts = []
                
                if text_suppression.get('suppressAllText', False):
                    no_text_prompts = text_suppression.get('noTextPrompts', [])
                    suppression_prompts.extend(no_text_prompts[:3])  # Use top 3
                    
                    text_prohibitions = text_suppression.get('textProhibitions', [])
                    if text_prohibitions:
                        suppression_prompts.append(f"Avoid: {', '.join(text_prohibitions[:5])}")
                
                # Combine prompts
                image_prompt_parts = [base_prompt] + suppression_prompts
                
                # Add content context
                title_context = idea.get('title', '')
                body_context = idea.get('body', '')
                if title_context:
                    image_prompt_parts.append(f"Context: {title_context}")
                
                image_prompt = " ".join(image_prompt_parts)
                print(f"📝 Applied text suppression prompt: {image_prompt[:100]}...")
                
            except Exception as e:
                print(f"❌ Error loading text suppression settings: {e}. Using basic prompt.")
                image_prompt = "Generate a professional, high-quality equipment rental image with no text overlays."
            
            # Generate images with text suppression
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
