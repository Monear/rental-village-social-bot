import os
import json
from sanity import Client
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from the project root .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

# Sanity client configuration
SANITY_PROJECT_ID = os.environ.get("SANITY_PROJECT_ID", "2pxuaj9k")
SANITY_DATASET = os.environ.get("SANITY_DATASET", "production")
SANITY_API_TOKEN = os.environ.get("SANITY_API_TOKEN") # Ensure this is set in your environment variables

# Mask the API token for logging
masked_token = SANITY_API_TOKEN[:4] + "..." + SANITY_API_TOKEN[-4:] if SANITY_API_TOKEN else "Not Set"
logger.info(f"Using Sanity Project ID: {SANITY_PROJECT_ID}, Dataset: {SANITY_DATASET}, API Token: {masked_token}")

client = Client(
    project_id=SANITY_PROJECT_ID,
    dataset=SANITY_DATASET,
    token=SANITY_API_TOKEN,
    use_cdn=False, # Set to False for fresh data during migration
    logger=logger
)

def get_prompt_type_from_filename(filename):
    """
    Infers prompt type from filename.
    """
    if "content_generation_prompt" in filename:
        return "contentGeneration"
    elif "image_generation_instructions" in filename:
        return "imageGeneration"
    elif "social_media_best_practices" in filename:
        return "socialMediaBestPractices"
    else:
        return "other"

def migrate_prompts(prompts_dir):
    """
    Migrates markdown prompt files to Sanity.
    """
    logger.info(f"Starting prompt migration from {prompts_dir}...")
    migrated_count = 0
    
    for filename in os.listdir(prompts_dir):
        if filename.endswith(".md"):
            file_path = os.path.join(prompts_dir, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                title = filename.replace("_", " ").replace(".md", "").title()
                prompt_type = get_prompt_type_from_filename(filename)
                doc_id = f"prompt-{os.path.splitext(filename)[0]}"

                sanity_document = {
                    "_type": "contentPrompt",
                    "_id": doc_id, # Unique ID for the document
                    "title": title,
                    "content": content,
                    "promptType": prompt_type,
                    "version": "1.0", # Default version
                    "active": True,
                }
                
                # Use client.mutate with createOrReplace transaction
                transactions = [{'createOrReplace': sanity_document}]
                result = client.mutate(transactions=transactions)
                logger.info(f"Mutate result for {filename}: {json.dumps(result, indent=2)}")

                # Read back to verify
                read_back_result = client.query(groq=f'*[_id == "{doc_id}"][0]')
                if read_back_result and read_back_result.get('result'):
                    logger.info(f"Successfully migrated and verified: {filename}")
                    migrated_count += 1
                else:
                    logger.error(f"Failed to verify {filename} after migration. Read back result: {read_back_result}")

            except Exception as e:
                logger.error(f"Error migrating {filename}: {e}")
    
    logger.info(f"Finished prompt migration. Migrated {migrated_count} prompts.")

if __name__ == "__main__":
    prompts_directory = os.path.join(os.path.dirname(__file__), '..', 'prompts')
    migrate_prompts(prompts_directory)