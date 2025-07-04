#!/usr/bin/env python3
"""
Containerized Sanity Data Fixer
This script fixes missing _key values and cleans up the equipment schema.
Designed to run in a container with no local dependencies.
"""

import os
import json
import uuid
import logging
from datetime import datetime
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_key() -> str:
    """Generate a unique key for array items."""
    return str(uuid.uuid4()).replace('-', '')[:12]

def add_keys_to_array(array_data: List[Any]) -> List[Dict[str, Any]]:
    """Add _key property to array items that don't have it."""
    if not array_data or not isinstance(array_data, list):
        return array_data
    
    fixed_array = []
    for item in array_data:
        if isinstance(item, dict):
            if '_key' not in item:
                item['_key'] = generate_key()
            fixed_array.append(item)
        elif isinstance(item, str):
            # Convert string array items to objects with keys
            fixed_array.append({
                '_key': generate_key(),
                'value': item
            })
        else:
            # For other types, wrap in object
            fixed_array.append({
                '_key': generate_key(),
                'value': item
            })
    
    return fixed_array

def fix_equipment_document(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Fix a single equipment document by adding missing keys and cleaning up."""
    fixed_doc = doc.copy()
    
    # Arrays that need _key properties
    array_fields = [
        'images', 'video_urls', 'manual_urls', 'specifications', 'categories',
        'subcategories', 'primary_use_cases', 'secondary_use_cases',
        'industries_served', 'project_types', 'related_products',
        'keywords', 'search_tags', 'ai_keywords', 'ai_suggested_use_cases',
        'ai_project_types'
    ]
    
    # Fix array fields
    for field in array_fields:
        if field in fixed_doc and fixed_doc[field]:
            if field == 'images':
                # Special handling for images
                images = fixed_doc[field]
                for img in images:
                    if isinstance(img, dict) and '_key' not in img:
                        img['_key'] = generate_key()
            elif field in ['categories', 'industries_served', 'keywords', 'search_tags', 
                          'ai_keywords', 'ai_suggested_use_cases', 'ai_project_types']:
                # These should remain as simple string arrays for the new schema
                # But we need to ensure they're clean
                if isinstance(fixed_doc[field], list):
                    # Clean up duplicates and empty values
                    fixed_doc[field] = list(set([str(item).strip() for item in fixed_doc[field] if item and str(item).strip()]))
            else:
                # Other arrays get keys added
                fixed_doc[field] = add_keys_to_array(fixed_doc[field])
    
    # Clean up and organize data for new schema
    # Remove fields not needed for content generation
    fields_to_remove = [
        'sku',  # Not needed for content generation
        'dimensions',  # Physical dimensions not essential for social media
        'next_available_date',  # Operational data, not content data
        'maintenance_schedule',  # Internal operations, not customer-facing
        'compliance_standards',  # Too technical for social media content
        'age_restrictions',  # Rarely used in content generation
        'review_count',  # Can be calculated if needed
        'review_rating',  # Can be calculated if needed  
        'search_tags'  # Duplicate of keywords - keeping keywords instead
    ]
    
    for field in fields_to_remove:
        if field in fixed_doc:
            del fixed_doc[field]
    
    # Ensure required fields exist
    if 'name' not in fixed_doc or not fixed_doc['name']:
        logger.warning(f"Document {fixed_doc.get('_id', 'unknown')} missing name")
        return None
    
    # Update timestamps
    fixed_doc['last_updated'] = datetime.now().isoformat()
    
    # Ensure proper structure for nested objects
    if 'pricing' in fixed_doc and fixed_doc['pricing']:
        pricing = fixed_doc['pricing']
        # Clean up pricing structure
        clean_pricing = {}
        if 'daily_rate' in pricing:
            clean_pricing['daily_rate'] = pricing['daily_rate']
        if 'weekly_rate' in pricing:
            clean_pricing['weekly_rate'] = pricing['weekly_rate']
        if 'monthly_rate' in pricing:
            clean_pricing['monthly_rate'] = pricing['monthly_rate']
        if 'currency' in pricing:
            clean_pricing['currency'] = pricing['currency']
        fixed_doc['pricing'] = clean_pricing
    
    if 'availability' in fixed_doc and fixed_doc['availability']:
        availability = fixed_doc['availability']
        clean_availability = {}
        if 'status' in availability:
            clean_availability['status'] = availability['status']
        if 'quantity_available' in availability:
            clean_availability['quantity_available'] = availability['quantity_available']
        fixed_doc['availability'] = clean_availability
    
    if 'safety' in fixed_doc and fixed_doc['safety']:
        safety = fixed_doc['safety']
        clean_safety = {}
        if 'operator_certification_required' in safety:
            clean_safety['operator_certification_required'] = safety['operator_certification_required']
        if 'safety_requirements' in safety:
            clean_safety['safety_requirements'] = safety['safety_requirements']
        fixed_doc['safety'] = clean_safety
    
    logger.info(f"Fixed document: {fixed_doc.get('name', 'Unknown')}")
    return fixed_doc

def main():
    """Main execution function."""
    try:
        # Import Sanity client
        from sanity import Client
        from dotenv import load_dotenv
        
        # Load environment variables
        load_dotenv()
        
        SANITY_PROJECT_ID = os.environ.get("SANITY_PROJECT_ID")
        SANITY_DATASET = os.environ.get("SANITY_DATASET") 
        SANITY_API_TOKEN = os.environ.get("SANITY_API_TOKEN")
        
        if not all([SANITY_PROJECT_ID, SANITY_DATASET, SANITY_API_TOKEN]):
            logger.error("Missing required environment variables")
            return False
        
        client = Client(
            project_id=SANITY_PROJECT_ID,
            dataset=SANITY_DATASET,
            token=SANITY_API_TOKEN,
            use_cdn=False,
            logger=logger
        )
        
        logger.info("🔍 Fetching all equipment documents...")
        
        # Fetch all equipment documents
        query = '*[_type == "equipment"]'
        equipment_docs = client.query(groq=query)
        
        if 'result' in equipment_docs:
            docs = equipment_docs['result']
        else:
            docs = equipment_docs
        
        logger.info(f"Found {len(docs)} equipment documents")
        
        if not docs:
            logger.warning("No equipment documents found")
            return True
        
        # Process each document
        fixed_count = 0
        for doc in docs:
            try:
                fixed_doc = fix_equipment_document(doc)
                if fixed_doc:
                    # Update the document in Sanity
                    transactions = [{'createOrReplace': fixed_doc}]
                    result = client.mutate(transactions=transactions)
                    
                    if result:
                        fixed_count += 1
                        logger.info(f"✅ Fixed: {fixed_doc.get('name', 'Unknown')}")
                    else:
                        logger.error(f"❌ Failed to update: {doc.get('name', 'Unknown')}")
                        
            except Exception as e:
                logger.error(f"❌ Error processing {doc.get('name', 'Unknown')}: {e}")
                continue
        
        logger.info(f"🎉 Successfully fixed {fixed_count}/{len(docs)} documents")
        return True
        
    except ImportError as e:
        logger.error(f"Missing dependencies: {e}")
        logger.info("This script should be run in a container with all dependencies installed")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)