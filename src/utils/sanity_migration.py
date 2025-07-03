import json
from sanity.client import Client
import os
import logging
from dotenv import load_dotenv

# Load environment variables from the project root .env file
load_dotenv(dotenv_path='/Users/tyler/Documents/rental_village/social_media/.env')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sanity client configuration
SANITY_PROJECT_ID = os.environ.get("SANITY_PROJECT_ID")
SANITY_DATASET = os.environ.get("SANITY_DATASET")
SANITY_API_TOKEN = os.environ.get("SANITY_API_TOKEN")

client = Client(
    project_id=SANITY_PROJECT_ID,
    dataset=SANITY_DATASET,
    token=SANITY_API_TOKEN,
    use_cdn=False,
    logger=logger
)

def migrate_equipment_catalog(json_file_path):
    """
    Migrates equipment data from a JSON file to Sanity.
    """
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)

        product_catalog = data.get("product_catalog", [])
        total_products = len(product_catalog)
        logger.info(f"Starting migration of {total_products} products...")

        for i, product in enumerate(product_catalog):
            product_name = product.get('name', 'Unknown Product')
            logger.info(f"Processing product {i+1}/{total_products}: {product_name}")
            
            # --- Data Transformation ---
            sanity_document = transform_product_to_sanity_format(product)
            logger.info(f"Transformed Sanity document: {json.dumps(sanity_document, indent=2)}")

            # --- Send to Sanity ---
            try:
                transactions = [{'createOrReplace': sanity_document}]
                logger.info(f"Attempting to mutate Sanity with transactions: {transactions}")
                result = client.mutate(transactions=transactions, return_documents=True)
                logger.info(f"Sanity mutate result for {product_name}: {json.dumps(result, indent=2)}")

                if result and result.get('results') and result['results'][0].get('document') and result['results'][0]['document'].get('_id'):
                    doc_id = result['results'][0]['document']['_id']
                    logger.info(f"Successfully migrated {product_name} to Sanity with ID: {doc_id}")
                else:
                    logger.warning(f"Failed to migrate {product_name} to Sanity: No document ID returned or unexpected result structure.")
            except Exception as e:
                logger.error(f"Error sending {product_name} to Sanity: {e}")

            # --- Progress Tracking ---
            if (i + 1) % 10 == 0 or (i + 1) == total_products:
                logger.info(f"Migrated {i+1}/{total_products} products.")

    except FileNotFoundError:
        logger.error(f"Error: JSON file not found at {json_file_path}")
    except json.JSONDecodeError:
        logger.error(f"Error: Could not decode JSON from {json_file_path}")
    except Exception as e:
        # --- Error Handling ---
        logger.error(f"An unexpected error occurred during migration: {e}")

def transform_product_to_sanity_format(product_data):
    """
    Transforms a single product dictionary into a Sanity document format.
    """
    transformed_doc = {
        "_type": "equipment", # Must match the name of your Sanity schema type
        "_id": product_data.get("id"), # Use a unique ID from your source data
        "name": product_data.get("name"),
        "slug": {
            "_type": "slug",
            "current": product_data.get("slug")
        },
        "categories": product_data.get("categories", []),
        "subcategories": product_data.get("subcategories", []),
        "short_description": product_data.get("short_description"),
        "full_description": product_data.get("full_description"),
        "technical_description": product_data.get("technical_description"),
        "images": [
            {"_type": "equipmentImage", "url": img.get("url"), "alt_text": img.get("alt_text"), "is_primary": img.get("is_primary"), "size": img.get("size")}
            for img in product_data.get("images", [])
        ],
        "video_urls": product_data.get("video_urls", []),
        "manual_urls": product_data.get("manual_urls", []),
        "specifications": [
            {"_type": "specification", "name": spec.get("name"), "value": str(spec.get("value")), "unit": spec.get("unit"), "category": spec.get("category")}
            for spec in product_data.get("specifications", [])
        ],
        "dimensions": product_data.get("dimensions", {}),
        "power_source": product_data.get("power_source"),
        "pricing": product_data.get("pricing", {}),
        "availability": product_data.get("availability", {}),
        "primary_use_cases": product_data.get("primary_use_cases", []),
        "secondary_use_cases": product_data.get("secondary_use_cases", []),
        "industries_served": product_data.get("industries_served", []),
        "project_types": product_data.get("project_types", []),
        "safety": product_data.get("safety", {}),
        "keywords": product_data.get("keywords", []),
        "search_tags": product_data.get("search_tags", []),
        "related_products": [], # This would require references, more complex
        "created_date": product_data.get("created_date"),
        "last_updated": product_data.get("last_updated"),
        "review_count": product_data.get("review_count"),
        "brand": product_data.get("brand"),
        "model": product_data.get("model"),
        "weight": product_data.get("weight"),
        "popularity_score": product_data.get("popularity_score"),
        "review_rating": product_data.get("review_rating"),
        "ai_suggested_use_cases": product_data.get("ai_suggested_use_cases", []),
        "ai_keywords": product_data.get("ai_keywords", []),
        "ai_project_types": product_data.get("ai_project_types", []),
    }

    # Handle potential None values for numbers
    for key in ["daily_rate", "weekly_rate", "monthly_rate", "deposit_required"]:
        if transformed_doc.get("pricing", {}).get(key) is None:
            transformed_doc["pricing"].pop(key, None)
    
    for key in ["review_count", "weight", "popularity_score", "review_rating", "age_restrictions"]:
        if transformed_doc.get(key) is None:
            transformed_doc.pop(key, None)

    # Handle datetime fields
    for key in ["created_date", "last_updated"]:
        if transformed_doc.get(key) == "":
            transformed_doc.pop(key, None)
    
    # Handle next_available_date in availability
    if transformed_doc.get("availability", {}).get("next_available_date") == "":
        transformed_doc["availability"].pop("next_available_date", None)

    return transformed_doc

if __name__ == "__main__":
    # Ensure you have mcp_rental_catalog_enhanced.json in src/data/
    json_path = "/Users/tyler/Documents/rental_village/social_media/src/data/mcp_rental_catalog_enhanced.json"
    migrate_equipment_catalog(json_path)