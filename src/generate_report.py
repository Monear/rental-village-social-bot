# src/generate_report.py
import os
from datetime import date
import notion_client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")

def get_this_months_posted_content(notion):
    """
    Retrieves all content posted in the current month that has performance metrics.
    """
    # Get the first day of the current month
    first_day_of_month = date.today().replace(day=1).isoformat()

    try:
        # This is a simplified query. A real query might need to handle pagination
        # for a large number of posts.
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
                            "on_or_after": first_day_of_month
                        }
                    },
                    {
                        "property": "Likes",
                        "number": {
                            "is_not_empty": True
                        }
                    }
                ]
            },
            sorts=[
                {
                    "property": "Likes",
                    "direction": "descending"
                }
            ]
        )
        return response.get("results", [])
    except Exception as e:
        print(f"Error querying Notion for monthly report data: {e}")
        return []

def create_markdown_report(posts):
    """
    Generates a Markdown-formatted report from the provided posts.
    """
    if not posts:
        return "# Monthly Performance Report\n\nNo posts with performance data found for this month."

    report_date = date.today().strftime("%B %Y")
    total_posts = len(posts)
    total_likes = sum(p['properties']['Likes']['number'] for p in posts)
    total_comments = sum(p['properties']['Comments']['number'] for p in posts)
    total_reach = sum(p['properties']['Reach']['number'] for p in posts)

    # Start building the Markdown string
    report = f"# Social Media Performance Report: {report_date}\n\n"
    report += "## 1. Executive Summary\n\n"
    report += f"- **Total Posts:** {total_posts}\n"
    report += f"- **Total Likes:** {total_likes}\n"
    report += f"- **Total Comments:** {total_comments}\n"
    report += f"- **Total Reach:** {total_reach}\n\n"
    report += "## 2. Top 3 Performing Posts (by Likes)\n\n"

    # Add the top 3 posts
    for i, post in enumerate(posts[:3]):
        post_name = post['properties']['Name']['title'][0]['text']['content']
        likes = post['properties']['Likes']['number']
        comments = post['properties']['Comments']['number']
        reach = post['properties']['Reach']['number']
        report += f"### {i+1}. {post_name}\n"
        report += f"- **Likes:** {likes}\n"
        report += f"- **Comments:** {comments}\n"
        report += f"- **Reach:** {reach}\n\n"
        
    report += "## 3. Key Takeaways & Recommendations\n\n"
    report += "- *(Human analysis needed here. What content pillars are performing best?)*\n"
    report += "- *(What was the ROI on ad spend this month?)*\n"
    report += "- *(Recommendation for next month's content focus.)*\n"

    return report

def save_report_to_file(report_content):
    """
    Saves the generated report to a file.
    """
    report_date = date.today().strftime("%Y-%m")
    file_name = f"monthly_report_{report_date}.md"
    file_path = os.path.join("strategy_documents", file_name) # Save it with the other strategy docs

    try:
        with open(file_path, "w") as f:
            f.write(report_content)
        print(f"Successfully saved report to {file_path}")
    except Exception as e:
        print(f"Error saving report file: {e}")


def main():
    """
    Main function to generate the monthly performance report.
    """
    if not NOTION_TOKEN or not DATABASE_ID:
        raise ValueError("NOTION_TOKEN and DATABASE_ID must be set in the .env file.")

    notion = notion_client.Client(auth=NOTION_TOKEN)

    print("Generating monthly performance report...")
    this_months_posts = get_this_months_posted_content(notion)
    
    report_content = create_markdown_report(this_months_posts)
    save_report_to_file(report_content)
    
    print("Report generation complete.")

if __name__ == "__main__":
    main()
