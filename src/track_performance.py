# src/track_performance.py
import os
from datetime import date, timedelta
import notion_client
from dotenv import load_dotenv
import random

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")
# In a real implementation, you would get these from your Facebook/Instagram Developer App
FACEBOOK_API_TOKEN = os.getenv("FACEBOOK_API_TOKEN")
INSTAGRAM_API_TOKEN = os.getenv("INSTAGRAM_API_TOKEN")


def get_posted_content_from_notion(notion):
    """
    Retrieves pages from Notion that have the 'Posted' status
    and haven't been updated with metrics yet.
    """
    # Look for posts made 3 days ago to allow time for engagement to build.
    target_date = (date.today() - timedelta(days=3)).isoformat()

    try:
        response = notion.databases.query(
            database_id=DATABASE_ID,
            filter={
                "and": [
                    {
                        "property": "Status",
                        "select": {
                            "equals": "Posted"
                        }
                    },
                    {
                        "property": "Post Date",
                        "date": {
                            "equals": target_date
                        }
                    },
                    {
                        "property": "Likes", # Assumes a 'Likes' number property exists
                        "number": {
                            "is_empty": True
                        }
                    }
                ]
            }
        )
        return response.get("results", [])
    except Exception as e:
        print(f"Error querying Notion for posted content: {e}")
        return []

def get_performance_metrics(post_id, platform):
    """
    Placeholder function to simulate fetching performance data from social media APIs.
    """
    print(f"Fetching metrics for post_id: {post_id} on platform: {platform}")
    # In a real implementation, you would make a call to the Facebook or Instagram Graph API here.
    # Example:
    # if platform == "Facebook":
    #     url = f"https://graph.facebook.com/v14.0/{post_id}/insights?metric=post_reactions_by_type_total,post_impressions"
    #     response = requests.get(url, params={"access_token": FACEBOOK_API_TOKEN})
    #     data = response.json()
    #     return {"likes": data['data'][0]['values'][0]['value']['like'], "comments": ..., "reach": ...}

    # For this draft, we'll return random data.
    return {
        "likes": random.randint(10, 150),
        "comments": random.randint(2, 25),
        "reach": random.randint(500, 5000)
    }

def update_notion_with_metrics(notion, page_id, metrics):
    """
    Updates a Notion page with the fetched performance metrics.
    """
    try:
        notion.pages.update(
            page_id=page_id,
            properties={
                "Likes": {"number": metrics.get("likes")},
                "Comments": {"number": metrics.get("comments")},
                "Reach": {"number": metrics.get("reach")}
                # Assumes 'Likes', 'Comments', and 'Reach' are number properties in Notion
            }
        )
        print(f"Successfully updated page {page_id} with metrics.")
    except Exception as e:
        print(f"Error updating Notion page {page_id}: {e}")


def main():
    """
    Main function to track performance of posted content.
    """
    if not NOTION_TOKEN or not DATABASE_ID:
        raise ValueError("NOTION_TOKEN and DATABASE_ID must be set in the .env file.")

    notion = notion_client.Client(auth=NOTION_TOKEN)
    
    print("Checking for posted content to track...")
    posts_to_track = get_posted_content_from_notion(notion)

    if not posts_to_track:
        print("No new posts to track.")
        return

    for post in posts_to_track:
        page_id = post.get("id")
        # Assumes a 'Platform' select property and a 'Post ID' text property exist
        platform = post.get("properties", {}).get("Platform", {}).get("select", {}).get("name")
        social_media_post_id = post.get("properties", {}).get("Post ID", {}).get("rich_text", [{}])[0].get("text", {}).get("content")

        if not platform or not social_media_post_id:
            print(f"Skipping page {page_id} due to missing Platform or Post ID.")
            continue

        metrics = get_performance_metrics(social_media_post_id, platform)
        update_notion_with_metrics(notion, page_id, metrics)

    print("Finished tracking performance.")

if __name__ == "__main__":
    main()
