# src/utils/check_notion_db.py
import os
import json
from notion_client import Client
from dotenv import load_dotenv

# Load environment variables from the root .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

def main():
    """
    Connects to the Notion API and prints the properties of the specified database.
    """
    if not NOTION_API_KEY or not NOTION_DATABASE_ID:
        raise ValueError("NOTION_API_KEY and NOTION_DATABASE_ID must be set in the .env file.")

    notion = Client(auth=NOTION_API_KEY)

    print(f"Fetching properties for database: {NOTION_DATABASE_ID}")

    try:
        db_info = notion.databases.retrieve(database_id=NOTION_DATABASE_ID)
        properties = db_info.get("properties", {})

        print("\n--- Database Properties ---")
        for name, details in properties.items():
            print(f"- Name: '{name}'")
            print(f"  Type: {details['type']}")
            if details['type'] in ["select", "multi_select"]:
                options = [opt['name'] for opt in details[details['type']]['options']]
                print(f"  Options: {options}")
        print("-------------------------\n")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
