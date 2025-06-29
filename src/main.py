import os
import notion_client
import requests
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")

def get_approved_content():
    """
    Retrieves approved content from the Notion database.
    """
    if not NOTION_TOKEN or not DATABASE_ID:
        raise ValueError("NOTION_TOKEN and DATABASE_ID must be set in the .env file.")

    notion = notion_client.Client(auth=NOTION_TOKEN)

    response = notion.databases.query(
        database_id=DATABASE_ID,
        filter={
            "and": [
                {
                    "property": "Status",
                    "select": {
                        "equals": "Approved"
                    }
                },
                {
                    "property": "Post Date",
                    "date": {
                        "on_or_before": "today"
                    }
                }
            ]
        }
    )
    return response.get("results")

def post_to_social_media(content):
    """
    Posts content to social media platforms.
    """
    # This is a placeholder function.
    # In a real-world scenario, this function would use the Facebook and Instagram APIs to post content.
    print(f"Posting to social media: {content}")

def update_notion_status(page_id):
    """
    Updates the status of a page in Notion.
    """
    notion = notion_client.Client(auth=NOTION_TOKEN)

    notion.pages.update(
        page_id=page_id,
        properties={
            "Status": {
                "select": {
                    "name": "Posted"
                }
            }
        }
    )

def main():
    """
    Main function.
    """
    approved_content = get_approved_content()

    for item in approved_content:
        content = item.get("properties").get("Content").get("rich_text")[0].get("text").get("content")
        page_id = item.get("id")

        post_to_social_media(content)
        update_notion_status(page_id)

if __name__ == "__main__":
    main()
