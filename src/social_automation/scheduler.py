"""
Social Media Scheduler

Handles scheduling and orchestration of social media posts with status tracking.
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta, timezone
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
import os
import signal
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from .facebook_poster import FacebookPoster, FacebookPost, create_facebook_poster
from .status_monitor import NotionStatusMonitor, NotionContent, create_status_monitor

logger = logging.getLogger(__name__)

class SocialMediaScheduler:
    """Orchestrates social media posting with Notion integration"""
    
    def __init__(self):
        """Initialize scheduler with required components"""
        self.facebook_poster = create_facebook_poster()
        self.status_monitor = create_status_monitor()
        self.scheduler = BackgroundScheduler()
        self.running = False
        
        # Validate connections
        if not self.facebook_poster.validate_token():
            raise ValueError("Facebook token validation failed")
        
        logger.info("Social media scheduler initialized successfully")
    
    def start(self):
        """Start the scheduler"""
        try:
            # Schedule monitoring jobs
            self.scheduler.add_job(
                func=self.process_ready_content,
                trigger=IntervalTrigger(minutes=5),  # Check every 5 minutes
                id='process_ready_content',
                name='Process Ready Content',
                replace_existing=True
            )
            
            self.scheduler.add_job(
                func=self.check_scheduled_posts,
                trigger=IntervalTrigger(minutes=10),  # Check every 10 minutes
                id='check_scheduled_posts',
                name='Check Scheduled Posts',
                replace_existing=True
            )
            
            self.scheduler.start()
            self.running = True
            logger.info("Social media scheduler started")
            
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
            raise
    
    def stop(self):
        """Stop the scheduler"""
        if self.running:
            self.scheduler.shutdown()
            self.running = False
            logger.info("Social media scheduler stopped")
    
    def process_ready_content(self):
        """Process content items ready for scheduling"""
        try:
            ready_items = self.status_monitor.get_ready_for_scheduling()
            
            for content in ready_items:
                if not self.status_monitor.validate_content(content):
                    logger.warning(f"Invalid content for page {content.page_id}, skipping")
                    continue
                
                # Only process Facebook content
                if content.platform.lower() != "facebook":
                    logger.info(f"Skipping non-Facebook content: {content.platform}")
                    continue
                
                success = self.schedule_post(content)
                if success:
                    logger.info(f"Successfully scheduled post for page {content.page_id}")
                else:
                    logger.error(f"Failed to schedule post for page {content.page_id}")
                    
        except Exception as e:
            logger.error(f"Error processing ready content: {e}")
    
    def schedule_post(self, content: NotionContent) -> bool:
        """
        Schedule a single post
        
        Args:
            content: NotionContent to schedule
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create Facebook post object
            facebook_post = FacebookPost(
                message=content.content,
                image_urls=content.images if content.images else None
            )
            
            # Determine posting strategy
            now = datetime.now(timezone.utc)
            if content.scheduled_time and content.scheduled_time > now:
                # Schedule for future posting
                scheduled_timestamp = int(content.scheduled_time.timestamp())
                facebook_post.scheduled_publish_time = scheduled_timestamp
                
                result = self.facebook_poster.create_post(facebook_post)
                
                if result.success:
                    # Update status to Scheduled
                    self.status_monitor.update_status(
                        content.page_id,
                        "Scheduled",
                        result.post_id
                    )
                    
                    # Schedule job to check when post is published
                    self.scheduler.add_job(
                        func=self.check_post_published,
                        trigger=DateTrigger(run_date=content.scheduled_time + timedelta(minutes=5)),
                        args=[content.page_id, result.post_id],
                        id=f'check_published_{content.page_id}',
                        replace_existing=True
                    )
                    
                    logger.info(f"Scheduled post for {content.scheduled_time}: {result.post_id}")
                    return True
                else:
                    logger.error(f"Failed to schedule post: {result.error_message}")
                    return False
            else:
                # Post immediately
                result = self.facebook_poster.create_post(facebook_post)
                
                if result.success:
                    # Update status to Posted
                    self.status_monitor.update_status(
                        content.page_id,
                        "Posted",
                        result.post_id
                    )
                    
                    logger.info(f"Posted immediately: {result.post_id}")
                    return True
                else:
                    logger.error(f"Failed to post immediately: {result.error_message}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error scheduling post for page {content.page_id}: {e}")
            return False
    
    def check_post_published(self, page_id: str, post_id: str):
        """
        Check if a scheduled post has been published
        
        Args:
            page_id: Notion page ID
            post_id: Facebook post ID
        """
        try:
            post_data = self.facebook_poster.get_post_status(post_id)
            
            if post_data:
                is_published = post_data.get("is_published", False)
                
                if is_published:
                    # Update status to Posted
                    self.status_monitor.update_status(page_id, "Posted", post_id)
                    logger.info(f"Post {post_id} published successfully")
                else:
                    # Schedule another check in 5 minutes
                    self.scheduler.add_job(
                        func=self.check_post_published,
                        trigger=DateTrigger(run_date=datetime.now() + timedelta(minutes=5)),
                        args=[page_id, post_id],
                        id=f'check_published_{page_id}',
                        replace_existing=True
                    )
                    logger.info(f"Post {post_id} still scheduled, checking again later")
            else:
                logger.error(f"Could not get status for post {post_id}")
                
        except Exception as e:
            logger.error(f"Error checking post published status: {e}")
    
    def check_scheduled_posts(self):
        """Check scheduled posts that might need status updates"""
        try:
            scheduled_items = self.status_monitor.get_scheduled_content()
            
            for content in scheduled_items:
                # Get Facebook post ID from content
                facebook_post_id = self._get_facebook_post_id_from_content(content)
                
                if facebook_post_id:
                    post_data = self.facebook_poster.get_post_status(facebook_post_id)
                    
                    if post_data and post_data.get("is_published", False):
                        # Update status to Posted
                        self.status_monitor.update_status(content.page_id, "Posted", facebook_post_id)
                        logger.info(f"Updated scheduled post {facebook_post_id} to Posted")
                        
        except Exception as e:
            logger.error(f"Error checking scheduled posts: {e}")
    
    def _get_facebook_post_id_from_content(self, content: NotionContent) -> Optional[str]:
        """
        Get Facebook post ID from Notion content
        
        Args:
            content: NotionContent object
            
        Returns:
            Facebook post ID if found, None otherwise
        """
        try:
            # Get full page data to extract Post ID
            page = self.status_monitor.notion_client.pages.retrieve(page_id=content.page_id)
            properties = page.get("properties", {})
            
            post_id_prop = properties.get("Post ID")
            if post_id_prop and post_id_prop.get("rich_text"):
                post_id = "".join([t.get("plain_text", "") for t in post_id_prop["rich_text"]])
                return post_id.strip() if post_id else None
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting Facebook post ID: {e}")
            return None
    
    def run_once(self):
        """Run scheduler jobs once (for testing)"""
        logger.info("Running scheduler jobs once...")
        self.process_ready_content()
        self.check_scheduled_posts()
        logger.info("Scheduler jobs completed")

def main():
    """Main function to run the scheduler"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        scheduler = SocialMediaScheduler()
        
        # Handle graceful shutdown
        def signal_handler(signum, frame):
            logger.info("Received shutdown signal")
            scheduler.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Start scheduler
        scheduler.start()
        
        # Keep the process running
        logger.info("Scheduler running. Press Ctrl+C to stop.")
        signal.pause()
        
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.error(f"Scheduler failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()