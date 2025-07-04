# utils/sanity_asset_helpers.py
"""Helper functions for uploading assets to Sanity."""

import os
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

SANITY_PROJECT_ID = os.environ.get("SANITY_PROJECT_ID", "2pxuaj9k")
SANITY_DATASET = os.environ.get("SANITY_DATASET", "production")
SANITY_API_TOKEN = os.environ.get("SANITY_API_TOKEN")

def upload_image_to_sanity(image_path: str) -> str:
    """
    Upload an image file to Sanity and return the asset URL.
    Returns the Sanity asset URL if successful, None otherwise.
    """
    try:
        if not os.path.exists(image_path):
            print(f"Image file not found: {image_path}")
            return None
            
        file_path = Path(image_path)
        file_name = file_path.name
        
        # Determine content type
        content_type_map = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.svg': 'image/svg+xml'
        }
        content_type = content_type_map.get(file_path.suffix.lower(), 'image/jpeg')
        
        # Sanity asset upload endpoint
        upload_url = f"https://{SANITY_PROJECT_ID}.api.sanity.io/v2021-06-07/assets/images/{SANITY_DATASET}"
        
        headers = {
            "Authorization": f"Bearer {SANITY_API_TOKEN}",
        }
        
        # Upload the file
        with open(image_path, 'rb') as f:
            files = {
                'file': (file_name, f, content_type)
            }
            
            response = requests.post(
                upload_url,
                headers=headers,
                files=files,
                timeout=60
            )
            
        if response.status_code == 200:
            result = response.json()
            asset_url = result.get('url')
            asset_id = result.get('_id')
            
            print(f"✅ Successfully uploaded image to Sanity: {asset_url}")
            return asset_url
        else:
            print(f"❌ Failed to upload image to Sanity: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error uploading image to Sanity: {e}")
        return None

def create_sanity_image_object(asset_url: str, alt_text: str = "", caption: str = "") -> dict:
    """
    Create a Sanity image object from an asset URL.
    """
    return {
        "_key": f"img_{hash(asset_url) % 1000000}",
        "url": asset_url,
        "alt_text": alt_text,
        "caption": caption
    }