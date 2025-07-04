

import os
import logging
from sanity import Client
import uuid
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sanity client configuration
SANITY_PROJECT_ID = os.environ.get("SANITY_PROJECT_ID")
SANITY_DATASET = os.environ.get("SANITY_DATASET")
SANITY_API_TOKEN = os.environ.get("SANITY_API_TOKEN")

def test_sanity_connection():
    logger.info("Starting Sanity connection tests...")

    if not SANITY_API_TOKEN:
        logger.error("SANITY_API_TOKEN environment variable is not set. Please set it before running tests.")
        return False

    try:
        client = Client(
            project_id=SANITY_PROJECT_ID,
            dataset=SANITY_DATASET,
            token=SANITY_API_TOKEN,
            use_cdn=False,
            logger=logger
        )
        logger.info("Sanity client initialized.")

        # Test 1: Read Operation (fetch all contentPrompt documents)
        logger.info("\n--- Test 1: Read All Content Prompts ---")
        try:
            query_result = client.query(groq='*[_type == "contentPrompt"]')
            prompts = query_result.get('result', [])
            if isinstance(prompts, list):
                if prompts:
                    logger.info(f"Successfully fetched {len(prompts)} contentPrompt documents.")
                    for prompt in prompts:
                        logger.info(f"  - Prompt Title: {prompt.get('title')}, ID: {prompt.get('_id')}")
                else:
                    logger.warning("No contentPrompt documents found.")
            else:
                logger.error(f"Read operation returned unexpected type: {type(prompts)}. Content: {prompts}")
                return False
        except Exception as e:
            logger.error(f"Read operation failed: {e}")
            return False

        # Test 2: Write Operation (create a dummy document)
        logger.info("\n--- Test 2: Write Operation (Create) ---")
        dummy_doc_id = f"test-doc-{uuid.uuid4()}"
        dummy_document = {
            "_type": "equipment", # Using an existing schema type for testing
            "_id": dummy_doc_id,
            "name": "Test Equipment",
            "slug": {"_type": "slug", "current": "test-equipment"},
            "short_description": "This is a dummy document for connection testing."
        }
        try:
            create_transactions = [{'create': dummy_document}]
            create_result = client.mutate(transactions=create_transactions, return_documents=True)
            
            if isinstance(create_result, dict):
                if create_result and create_result.get('results') and create_result['results'][0].get('document') and create_result['results'][0]['document'].get('_id'):
                    logger.info(f"Successfully created dummy document with ID: {create_result['results'][0]['document']['_id']}")
                else:
                    logger.error(f"Failed to create dummy document. Unexpected result structure: {create_result}")
                    return False
            else:
                logger.error(f"Write operation (create) returned unexpected type: {type(create_result)}. Content: {create_result}")
                return False
        except Exception as e:
            logger.error(f"Write operation (create) failed: {e}")
            return False

        # Test 3: Delete Operation (delete the dummy document)
        logger.info("\n--- Test 3: Write Operation (Delete) ---")
        try:
            delete_transactions = [{'delete': {'id': dummy_doc_id}}]
            delete_result = client.mutate(transactions=delete_transactions)
            if isinstance(delete_result, dict):
                logger.info(f"Successfully deleted dummy document with ID: {dummy_doc_id}. Result: {delete_result}")
            else:
                logger.error(f"Delete operation returned unexpected type: {type(delete_result)}. Content: {delete_result}")
                return False
        except Exception as e:
            logger.error(f"Write operation (delete) failed: {e}")
            return False

        logger.info("\nAll Sanity connection tests passed successfully.")
        return True

    except Exception as e:
        logger.error(f"An error occurred during Sanity connection test: {e}")
        return False

if __name__ == "__main__":
    test_sanity_connection()
