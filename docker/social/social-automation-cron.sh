#!/bin/bash

# Social Media Automation Cron Script
# Runs every 5 minutes to check for posts ready for scheduling

set -e

# Set PATH to include Python location
export PATH=/usr/local/bin:/usr/bin:/bin:$PATH

# Change to app directory
cd /app

# Source environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Set Python path
export PYTHONPATH=/app/src:/app:$PYTHONPATH

# Log execution
echo "$(date): Starting social media automation check..."

# Run the automation check
/usr/local/bin/python3 -c "
import sys
import os
sys.path.insert(0, '/app/src')

from social_automation.scheduler import SocialMediaScheduler
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

try:
    scheduler = SocialMediaScheduler()
    scheduler.run_once()
    print('$(date): Social media automation check completed successfully')
except Exception as e:
    print(f'$(date): ERROR - Social media automation failed: {e}')
    sys.exit(1)
"

echo "$(date): Social media automation check finished."