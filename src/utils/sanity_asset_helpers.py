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

def upload_image_to_sanity(image_path: str) -> dict:
    """
    Upload an image file to Sanity and return the asset data.
    Returns the Sanity asset data if successful, None otherwise.
    """
    try:
        if not os.path.exists(image_path):
            print(f"Image file not found: {image_path}")
            return None
            
        file_path = Path(image_path)
        
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
        
        # Import the Sanity client
        from sanity import Client
        import logging
        
        # Create logger for the client
        logger = logging.getLogger(__name__)
        
        # Create a proper Sanity client instance
        sanity_client = Client(
            logger=logger,
            project_id=SANITY_PROJECT_ID,
            dataset=SANITY_DATASET,
            token=SANITY_API_TOKEN,
            use_cdn=False
        )
        
        print(f"📤 Uploading image to Sanity: {image_path}")
        print(f"   File size: {os.path.getsize(image_path)} bytes")
        print(f"   Content type: {content_type}")
        
        # Upload the file using the client's assets method
        result = sanity_client.assets(file_path=image_path, mime_type=content_type)
        
        if result:
            # Try to extract URL and ID from various possible result structures
            asset_url = None
            asset_id = None
            
            if isinstance(result, dict):
                # Check if there's a 'document' key (OmniPro-Group/sanity-python format)
                if 'document' in result:
                    doc = result['document']
                    asset_url = doc.get('url')
                    asset_id = doc.get('_id')
                    
                    # Check alternative key names in document
                    if not asset_url:
                        asset_url = doc.get('assetUrl') or doc.get('asset_url')
                    if not asset_id:
                        asset_id = doc.get('assetId') or doc.get('asset_id') or doc.get('id')
                
                # Standard dictionary response (fallback)
                if not asset_url:
                    asset_url = result.get('url')
                if not asset_id:
                    asset_id = result.get('_id')
                    
                # Check alternative key names at root level
                if not asset_url:
                    asset_url = result.get('assetUrl') or result.get('asset_url')
                if not asset_id:
                    asset_id = result.get('assetId') or result.get('asset_id') or result.get('id')
                    
            elif isinstance(result, str):
                # If result is a string, it might be the URL or ID
                if result.startswith('http'):
                    asset_url = result
                else:
                    asset_id = result
            
            print(f"✅ Successfully uploaded image to Sanity")
            print(f"   Asset URL: {asset_url}")
            print(f"   Asset ID: {asset_id}")
            return {"url": asset_url, "asset_id": asset_id}
        else:
            print(f"❌ Failed to upload image to Sanity: No result returned")
            return None
            
    except Exception as e:
        print(f"❌ Error uploading image to Sanity: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_sanity_image_object(asset_data, alt_text: str = "", caption: str = "") -> dict:
    """
    Create a Sanity image object from asset data (URL or dict with url/asset_id).
    """
    import uuid
    
    # Handle both string URLs and dict responses from upload_image_to_sanity
    if isinstance(asset_data, str):
        asset_url = asset_data
        asset_id = None
    else:
        asset_url = asset_data.get('url') if asset_data else None
        asset_id = asset_data.get('asset_id') if asset_data else None
    
    return {
        "_type": "image",
        "_key": str(uuid.uuid4()),  # Use UUID for unique keys
        "asset": {
            "_type": "reference",
            "_ref": asset_id if asset_id else str(uuid.uuid4())
        },
        "alt": alt_text,
        "caption": caption
    }