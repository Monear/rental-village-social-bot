#!/usr/bin/env python3
"""
Cron-based Social Media Automation Runner

Alternative to the continuous scheduler - runs once and exits.
Perfect for cron jobs and container environments.
"""

import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from social_automation.scheduler import SocialMediaScheduler

def setup_logging():
    """Setup logging for cron execution"""
    log_dir = "/app/logs"
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f"social_automation_{datetime.now().strftime('%Y%m%d')}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

def check_environment():
    """Check required environment variables"""
    required_vars = [
        "NOTION_TOKEN",
        "DATABASE_ID", 
        "FACEBOOK_PAGE_ACCESS_TOKEN",
        "FACEBOOK_PAGE_ID"
    ]
    
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logging.error(f"Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    return True

def main():
    """Main cron function"""
    setup_logging()
    
    logging.info("=== Social Media Automation Cron Job Started ===")
    
    # Check environment
    if not check_environment():
        logging.error("Environment check failed. Exiting.")
        sys.exit(1)
    
    try:
        # Create and run scheduler once
        scheduler = SocialMediaScheduler()
        scheduler.run_once()
        
        logging.info("=== Social Media Automation Cron Job Completed Successfully ===")
        
    except Exception as e:
        logging.error(f"Social media automation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()