"""
Notion Status Monitor for Social Media Automation

Monitors Notion database for content ready for scheduling and manages status updates.
"""

import logging
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from notion_client import Client

logger = logging.getLogger(__name__)

@dataclass
class NotionContent:
    """Notion content item ready for posting"""
    page_id: str
    title: str
    content: str
    images: List[str]
    status: str
    scheduled_time: Optional[datetime] = None
    platform: str = "Facebook"
    
class NotionStatusMonitor:
    """Monitor Notion database for content status changes"""
    
    def __init__(self, database_id: str):
        """
        Initialize status monitor
        
        Args:
            database_id: Notion database ID to monitor
        """
        self.database_id = database_id
        notion_token = os.getenv("NOTION_TOKEN")
        if not notion_token:
            raise ValueError("NOTION_TOKEN not found in environment variables")
        self.notion_client = Client(auth=notion_token)
        
    def get_ready_for_scheduling(self) -> List[NotionContent]:
        """
        Get all content items with 'Ready for Scheduling' status
        
        Returns:
            List of NotionContent items ready for scheduling
        """
        try:
            # Query for pages with "Ready for Scheduling" status
            query_filter = {
                "property": "Status",
                "status": {
                    "equals": "Ready for Scheduling"
                }
            }
            
            response = self.notion_client.databases.query(
                database_id=self.database_id,
                filter=query_filter
            )
            
            results = response.get("results", [])
            
            content_items = []
            for page in results:
                content_item = self._parse_notion_page(page)
                if content_item:
                    content_items.append(content_item)
            
            logger.info(f"Found {len(content_items)} items ready for scheduling")
            return content_items
            
        except Exception as e:
            logger.error(f"Failed to get ready for scheduling items: {e}")
            return []
    
    def get_scheduled_content(self) -> List[NotionContent]:
        """
        Get all content items with 'Scheduled' status
        
        Returns:
            List of NotionContent items that are scheduled
        """
        try:
            query_filter = {
                "property": "Status",
                "status": {
                    "equals": "Scheduled"
                }
            }
            
            response = self.notion_client.databases.query(
                database_id=self.database_id,
                filter=query_filter
            )
            
            results = response.get("results", [])
            
            content_items = []
            for page in results:
                content_item = self._parse_notion_page(page)
                if content_item:
                    content_items.append(content_item)
            
            logger.info(f"Found {len(content_items)} scheduled items")
            return content_items
            
        except Exception as e:
            logger.error(f"Failed to get scheduled items: {e}")
            return []
    
    def update_status(self, page_id: str, new_status: str, facebook_post_id: str = None) -> bool:
        """
        Update page status in Notion
        
        Args:
            page_id: Notion page ID
            new_status: New status value
            facebook_post_id: Optional Facebook post ID to store
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Update status (status type property)
            properties = {
                "Status": {"status": {"name": new_status}}
            }
            
            # Update Post ID if provided (rich_text type)
            if facebook_post_id:
                properties["Post ID"] = {"rich_text": [{"text": {"content": facebook_post_id}}]}
            
            response = self.notion_client.pages.update(
                page_id=page_id,
                properties=properties
            )
            
            logger.info(f"Updated page {page_id} status to {new_status}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update status for page {page_id}: {e}")
            return False
    
    def _parse_notion_page(self, page: Dict) -> Optional[NotionContent]:
        """
        Parse Notion page data into NotionContent object
        
        Args:
            page: Notion page object
            
        Returns:
            NotionContent object or None if parsing fails
        """
        try:
            properties = page.get("properties", {})
            
            # Extract title from "Name" property (title type)
            title_prop = properties.get("Name")
            title = ""
            if title_prop and title_prop.get("title"):
                title = "".join([t.get("plain_text", "") for t in title_prop["title"]])
            
            # Extract content from "Copy" property (rich_text type)
            content_prop = properties.get("Copy")
            content = ""
            if content_prop and content_prop.get("rich_text"):
                content = "".join([t.get("plain_text", "") for t in content_prop["rich_text"]])
            
            # Extract status from "Status" property (status type)
            status_prop = properties.get("Status")
            status = ""
            if status_prop and status_prop.get("status"):
                status = status_prop["status"].get("name", "")
            
            # Extract images from "Creative" property (files type)
            images = []
            image_prop = properties.get("Creative")
            if image_prop and image_prop.get("files"):
                for file_info in image_prop["files"]:
                    if file_info.get("type") == "external":
                        images.append(file_info["external"]["url"])
                    elif file_info.get("type") == "file":
                        images.append(file_info["file"]["url"])
            
            # Extract scheduled time from "Post Date" property (date type)
            scheduled_time = None
            schedule_prop = properties.get("Post Date")
            if schedule_prop and schedule_prop.get("date"):
                try:
                    scheduled_time = datetime.fromisoformat(
                        schedule_prop["date"]["start"].replace("Z", "+00:00")
                    )
                except ValueError:
                    logger.warning(f"Invalid scheduled time format in page {page['id']}")
            
            # Extract platform from "Platform" property (select type)
            platform = "Facebook"  # Default
            platform_prop = properties.get("Platform")
            if platform_prop and platform_prop.get("select"):
                platform = platform_prop["select"].get("name", "Facebook")
            
            return NotionContent(
                page_id=page["id"],
                title=title,
                content=content,
                images=images,
                status=status,
                scheduled_time=scheduled_time,
                platform=platform
            )
            
        except Exception as e:
            logger.error(f"Failed to parse Notion page {page.get('id', 'unknown')}: {e}")
            return None
    
    def validate_content(self, content: NotionContent) -> bool:
        """
        Validate content item has required fields for posting
        
        Args:
            content: NotionContent to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not content.content.strip():
            logger.warning(f"Content is empty for page {content.page_id}")
            return False
        
        if len(content.content) > 2000:  # Facebook character limit
            logger.warning(f"Content too long for page {content.page_id}")
            return False
        
        # Validate image URLs if present
        for image_url in content.images:
            if not image_url.startswith(('http://', 'https://')):
                logger.warning(f"Invalid image URL in page {content.page_id}: {image_url}")
                return False
        
        return True

def create_status_monitor() -> NotionStatusMonitor:
    """Create status monitor instance from environment variables"""
    database_id = os.getenv("DATABASE_ID")
    
    if not database_id:
        raise ValueError("DATABASE_ID not found in environment variables")
    
    return NotionStatusMonitor(database_id)