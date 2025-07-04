"""
Facebook Graph API Integration for Automated Posting

Handles Facebook page posting with image support and error handling.
"""

import os
import requests
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

@dataclass
class FacebookPost:
    """Facebook post data structure"""
    message: str
    image_urls: List[str] = None
    link: str = None
    scheduled_publish_time: Optional[int] = None
    
@dataclass
class PostResult:
    """Result of Facebook posting operation"""
    success: bool
    post_id: Optional[str] = None
    error_message: Optional[str] = None
    response_data: Optional[Dict] = None

class FacebookPoster:
    """Facebook Graph API integration for automated posting"""
    
    def __init__(self, page_access_token: str, page_id: str):
        """
        Initialize Facebook poster
        
        Args:
            page_access_token: Facebook page access token
            page_id: Facebook page ID
        """
        self.page_access_token = page_access_token
        self.page_id = page_id
        self.base_url = "https://graph.facebook.com/v18.0"
        
    def validate_token(self) -> bool:
        """Validate Facebook access token"""
        try:
            url = f"{self.base_url}/me"
            params = {"access_token": self.page_access_token}
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Token validated for page: {data.get('name', 'Unknown')}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Token validation failed: {e}")
            return False
    
    def upload_photo(self, image_url: str, caption: str = "") -> Optional[str]:
        """
        Upload photo to Facebook page
        
        Args:
            image_url: URL of image to upload
            caption: Optional caption for the image
            
        Returns:
            Photo ID if successful, None otherwise
        """
        try:
            url = f"{self.base_url}/{self.page_id}/photos"
            
            params = {
                "access_token": self.page_access_token,
                "url": image_url,
                "caption": caption,
                "published": "false"  # Upload unpublished for use in posts
            }
            
            response = requests.post(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            photo_id = data.get("id")
            
            if photo_id:
                logger.info(f"Photo uploaded successfully: {photo_id}")
                return photo_id
            else:
                logger.error("No photo ID returned from upload")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Photo upload failed: {e}")
            return None
    
    def create_post(self, post: FacebookPost) -> PostResult:
        """
        Create Facebook post
        
        Args:
            post: FacebookPost object with content
            
        Returns:
            PostResult with success status and details
        """
        try:
            url = f"{self.base_url}/{self.page_id}/feed"
            
            # Base parameters
            params = {
                "access_token": self.page_access_token,
                "message": post.message
            }
            
            # Add link if provided
            if post.link:
                params["link"] = post.link
            
            # Add scheduled publish time if provided
            if post.scheduled_publish_time:
                params["scheduled_publish_time"] = post.scheduled_publish_time
                params["published"] = "false"
            
            # Handle image attachments
            if post.image_urls:
                if len(post.image_urls) == 1:
                    # Single image post
                    photo_id = self.upload_photo(post.image_urls[0], post.message)
                    if photo_id:
                        # Use photo endpoint for single image
                        url = f"{self.base_url}/{self.page_id}/photos"
                        params = {
                            "access_token": self.page_access_token,
                            "url": post.image_urls[0],
                            "caption": post.message
                        }
                        
                        if post.scheduled_publish_time:
                            params["scheduled_publish_time"] = post.scheduled_publish_time
                            params["published"] = "false"
                else:
                    # Multiple images - create album
                    return self._create_album_post(post)
            
            # Make the request
            response = requests.post(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            post_id = data.get("id") or data.get("post_id")
            
            if post_id:
                logger.info(f"Post created successfully: {post_id}")
                return PostResult(
                    success=True,
                    post_id=post_id,
                    response_data=data
                )
            else:
                logger.error("No post ID returned from creation")
                return PostResult(
                    success=False,
                    error_message="No post ID returned",
                    response_data=data
                )
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Post creation failed: {e}")
            return PostResult(
                success=False,
                error_message=str(e)
            )
    
    def _create_album_post(self, post: FacebookPost) -> PostResult:
        """Create post with multiple images (album)"""
        try:
            # Upload all photos first
            photo_ids = []
            for image_url in post.image_urls:
                photo_id = self.upload_photo(image_url)
                if photo_id:
                    photo_ids.append(photo_id)
            
            if not photo_ids:
                return PostResult(
                    success=False,
                    error_message="Failed to upload any photos for album"
                )
            
            # Create album post
            url = f"{self.base_url}/{self.page_id}/feed"
            
            # Format attached media
            attached_media = [{"media_fbid": photo_id} for photo_id in photo_ids]
            
            params = {
                "access_token": self.page_access_token,
                "message": post.message,
                "attached_media": json.dumps(attached_media)
            }
            
            if post.scheduled_publish_time:
                params["scheduled_publish_time"] = post.scheduled_publish_time
                params["published"] = "false"
            
            response = requests.post(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            post_id = data.get("id")
            
            if post_id:
                logger.info(f"Album post created successfully: {post_id}")
                return PostResult(
                    success=True,
                    post_id=post_id,
                    response_data=data
                )
            else:
                return PostResult(
                    success=False,
                    error_message="No post ID returned from album creation",
                    response_data=data
                )
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Album post creation failed: {e}")
            return PostResult(
                success=False,
                error_message=str(e)
            )
    
    def get_post_status(self, post_id: str) -> Optional[Dict]:
        """
        Get post status and details
        
        Args:
            post_id: Facebook post ID
            
        Returns:
            Post data if successful, None otherwise
        """
        try:
            url = f"{self.base_url}/{post_id}"
            params = {
                "access_token": self.page_access_token,
                "fields": "id,message,created_time,is_published,scheduled_publish_time,status_type"
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get post status: {e}")
            return None
    
    def delete_post(self, post_id: str) -> bool:
        """
        Delete Facebook post
        
        Args:
            post_id: Facebook post ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            url = f"{self.base_url}/{post_id}"
            params = {"access_token": self.page_access_token}
            
            response = requests.delete(url, params=params)
            response.raise_for_status()
            
            logger.info(f"Post deleted successfully: {post_id}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to delete post: {e}")
            return False

def create_facebook_poster() -> FacebookPoster:
    """Create Facebook poster instance from environment variables"""
    page_access_token = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")
    page_id = os.getenv("FACEBOOK_PAGE_ID")
    
    if not page_access_token or not page_id:
        raise ValueError("Facebook credentials not found in environment variables")
    
    return FacebookPoster(page_access_token, page_id)