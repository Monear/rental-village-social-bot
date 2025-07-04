
import os
import json
import logging
from datetime import datetime
from sanity import Client
from dotenv import load_dotenv
import uuid
from src.utils.sanity_asset_helpers import upload_image_to_sanity, create_sanity_image_object

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sanity client configuration
SANITY_PROJECT_ID = os.environ.get("SANITY_PROJECT_ID", "2pxuaj9k")
SANITY_DATASET = os.environ.get("SANITY_DATASET", "production")
SANITY_API_TOKEN = os.environ.get("SANITY_API_TOKEN") # Ensure this is set in your environment variables

sanity_client = Client(
    project_id=SANITY_PROJECT_ID,
    dataset=SANITY_DATASET,
    token=SANITY_API_TOKEN,
    use_cdn=False, # Use CDN for fresh data when writing
    logger=logger
)

def save_social_content_to_sanity(idea: dict) -> str | None:
    """
    Saves a generated social media content idea to Sanity.
    Returns the Sanity document ID if successful, None otherwise.
    """
    try:
        # Convert equipment data to Sanity references
        equipment_references = []
        if idea.get("related_equipment"):
            for equipment in idea["related_equipment"]:
                if equipment.get("_id"):
                    equipment_references.append({
                        "_type": "reference",
                        "_ref": equipment["_id"]
                    })

        # Use real equipment images (no upload needed - they're already on CDN)
        image_data = []
        equipment_images = idea.get("equipment_images", [])
        for img in equipment_images:
            image_obj = create_sanity_image_object(
                asset_url=img['url'],
                alt_text=img['alt_text'],
                caption=img['caption']
            )
            image_data.append(image_obj)
        
        if image_data:
            print(f"✅ Using {len(image_data)} real equipment images")

        # Map the idea dictionary to the Sanity socialContent schema
        sanity_document = {
            "_type": "socialContent",
            "_id": str(uuid.uuid4()), # Generate a unique ID
            "title": idea.get("title"),
            "body": idea.get("body"),
            "content_pillar": idea.get("content_pillar", "general_content"),
            "keywords": idea.get("keywords", ""),
            "platform": idea.get("platform", "Multi-platform"),
            "status": "generated",
            "performance_metrics": {},
            "images": image_data,
            "related_equipment": equipment_references,
            "ai_generation_metadata": {
                "model_used": "gemini-1.5-flash",
                "temperature": 0.7,
                "timestamp": datetime.now().isoformat()
            },
        }

        # Use createOrReplace to handle potential re-runs or updates
        transactions = [{'createOrReplace': sanity_document}]
        result = sanity_client.mutate(transactions=transactions)
        logger.info(f"Sanity mutate result for social content: {json.dumps(result, indent=2)}")
        
        # Debugging: Print the full result structure
        logger.info(f"Full mutate result structure: {result}")

        if result and result.get('results') and result['results'][0].get('operation') in ['create', 'update']:
            doc_id = sanity_document['_id'] # Use the ID generated earlier
            logger.info(f"Successfully saved social content to Sanity with ID: {doc_id}")
            return doc_id
        else:
            logger.error(f"Failed to save social content to Sanity: Unexpected result structure or operation: {result}")
            return None

    except Exception as e:
        logger.error(f"Error saving social content to Sanity: {e}")
        return None
