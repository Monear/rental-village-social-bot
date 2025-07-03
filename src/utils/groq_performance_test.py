

import os
import time
import logging
from sanity.client import Client
from dotenv import load_dotenv

load_dotenv(dotenv_path='/Users/tyler/Documents/rental_village/social_media/.env')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SANITY_PROJECT_ID = os.environ.get("SANITY_PROJECT_ID")
SANITY_DATASET = os.environ.get("SANITY_DATASET")
SANITY_API_TOKEN = os.environ.get("SANITY_API_TOKEN")

client = Client(
    project_id=SANITY_PROJECT_ID,
    dataset=SANITY_DATASET,
    token=SANITY_API_TOKEN,
    use_cdn=True, # Use CDN for read operations
    logger=logger
)

def run_groq_query(query_name, groq_query):
    logger.info(f"Running GROQ query: {query_name}")
    start_time = time.time()
    try:
        result = client.query(groq=groq_query)
        end_time = time.time()
        duration = (end_time - start_time) * 1000 # milliseconds
        logger.info(f"Query '{query_name}' completed in {duration:.2f} ms. Results count: {len(result.get('result', []))}")
        return result
    except Exception as e:
        logger.error(f"Error running query '{query_name}': {e}")
        return None

if __name__ == "__main__":
    logger.info("Starting GROQ query performance tests...")

    # Test 1: Fetch all equipment (limited to 100 for initial test)
    run_groq_query("Fetch All Equipment (Limited)", "*[_type == \"equipment\"][0...100]")

    # Test 2: Fetch a specific equipment by ID
    # Replace with an actual ID from your migrated data if known, or fetch one dynamically
    # For now, using a placeholder ID
    run_groq_query("Fetch Specific Equipment by ID", "*[_type == \"equipment\" && _id == \"545573\"][0]")

    # Test 3: Fetch content prompts
    run_groq_query("Fetch All Content Prompts", "*[_type == \"contentPrompt\"]")

    # Test 4: Fetch equipment by category (example)
    run_groq_query("Fetch Equipment by Category (Lawn & Garden)", "*[_type == \"equipment\" && \"Lawn & Garden\" in categories]")

    logger.info("GROQ query performance tests finished.")

