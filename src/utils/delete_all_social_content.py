#!/usr/bin/env python3
"""
One-time script to delete ALL social content from Sanity for testing cleanup.
WARNING: This will permanently delete all socialContent documents!
"""

import os
import sys
from dotenv import load_dotenv
from sanity import Client
import logging

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sanity client configuration
SANITY_PROJECT_ID = os.environ.get("SANITY_PROJECT_ID", "2pxuaj9k")
SANITY_DATASET = os.environ.get("SANITY_DATASET", "production")
SANITY_API_TOKEN = os.environ.get("SANITY_API_TOKEN")

sanity_client = Client(
    project_id=SANITY_PROJECT_ID,
    dataset=SANITY_DATASET,
    token=SANITY_API_TOKEN,
    use_cdn=False,  # Use write API, not CDN
    logger=logger
)

def delete_all_social_content():
    """Delete all socialContent documents from Sanity."""
    
    print("🔍 Fetching all socialContent documents...")
    
    try:
        # Get all socialContent document IDs
        query_result = sanity_client.query(
            '*[_type == "socialContent"] { _id }'
        )
        
        social_content_docs = query_result.get('result', [])
        
        if not social_content_docs:
            print("✅ No socialContent documents found. Nothing to delete.")
            return
        
        print(f"📋 Found {len(social_content_docs)} socialContent documents")
        
        # Confirm deletion
        response = input(f"⚠️  Are you sure you want to delete ALL {len(social_content_docs)} socialContent documents? (yes/no): ")
        
        if response.lower() != 'yes':
            print("❌ Deletion cancelled.")
            return
        
        print("🗑️  Deleting all socialContent documents...")
        
        # Create delete transactions
        transactions = []
        for doc in social_content_docs:
            doc_id = doc['_id']
            transactions.append({
                'delete': {'id': doc_id}
            })
            print(f"   🗑️  Queued for deletion: {doc_id}")
        
        # Execute deletion in batches (Sanity has transaction limits)
        batch_size = 100
        total_deleted = 0
        
        for i in range(0, len(transactions), batch_size):
            batch = transactions[i:i + batch_size]
            print(f"🔄 Deleting batch {i//batch_size + 1} ({len(batch)} documents)...")
            
            try:
                result = sanity_client.mutate(transactions=batch)
                if result:
                    total_deleted += len(batch)
                    print(f"   ✅ Batch {i//batch_size + 1} deleted successfully")
                else:
                    print(f"   ❌ Failed to delete batch {i//batch_size + 1}")
            except Exception as e:
                print(f"   ❌ Error deleting batch {i//batch_size + 1}: {e}")
        
        print(f"🎉 Deletion complete! {total_deleted} documents deleted.")
        print("🔄 You may need to refresh your Sanity Studio to see the changes.")
        
    except Exception as e:
        print(f"❌ Error during deletion: {e}")

if __name__ == "__main__":
    print("🚨 DANGER: This will delete ALL socialContent documents from Sanity!")
    print("🚨 This action cannot be undone!")
    print()
    delete_all_social_content()