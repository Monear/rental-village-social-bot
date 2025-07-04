# src/suggest_content.py
import os
import sys
import argparse
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.general import read_file_content
from src.utils.gemini_helpers import generate_ideas_with_gemini, generate_image_with_gemini, generate_enhanced_image_with_real_equipment
from src.utils.notion_helpers import add_idea_to_notion, get_existing_notion_ideas
from src.utils.sanity_helpers import save_social_content_to_sanity
from src.utils.safety_validator import validate_idea_safety
import notion_client
import json
import logging
from sanity import Client
import requests

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'), override=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuration ---
NOTION_API_KEY = os.getenv("NOTION_TOKEN")
NOTION_DATABASE_ID = os.getenv("DATABASE_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Sanity client configuration
SANITY_PROJECT_ID = os.environ.get("SANITY_PROJECT_ID", "2pxuaj9k")
SANITY_DATASET = os.environ.get("SANITY_DATASET", "production")
SANITY_API_TOKEN = os.environ.get("SANITY_API_TOKEN") # Ensure this is set in your environment variables

sanity_client = Client(
    project_id=SANITY_PROJECT_ID,
    dataset=SANITY_DATASET,
    token=SANITY_API_TOKEN,
    use_cdn=True, # Use CDN for faster reads
    logger=logger
)

def main():
    parser = argparse.ArgumentParser(description="Generate social media content ideas and add them to Notion.")
    parser.add_argument("--num-ideas", type=int, default=3, help="Number of content ideas to generate.")
    parser.add_argument("--input-text", type=str, help="Pasted text to use as inspiration for idea generation.")
    args = parser.parse_args()

    if not all([NOTION_API_KEY, NOTION_DATABASE_ID, GEMINI_API_KEY, SANITY_API_TOKEN]):
        raise ValueError("Required API keys (NOTION, GEMINI, SANITY) must be set in the .env file.")

    # Fetch content guidelines from Sanity
    try:
        query_result = sanity_client.query(
            groq='*[_type == "contentPrompt" && title == "Content Generation Prompt"][0]'
        )
        content_guidelines_doc = query_result.get('result')
        content_guidelines = content_guidelines_doc.get('content') if content_guidelines_doc else ""
        if not content_guidelines:
            print("Error: Content generation prompt not found in Sanity.")
            return
    except Exception as e:
        print(f"Error fetching content guidelines from Sanity: {e}")
        return

    # Fetch social media best practices from Sanity
    try:
        query_result = sanity_client.query(
            groq='*[_type == "contentPrompt" && title == "Social Media Best Practices"][0]'
        )
        social_media_best_practices_doc = query_result.get('result')
        social_media_best_practices = social_media_best_practices_doc.get('content') if social_media_best_practices_doc else ""
        if not social_media_best_practices:
            print("Warning: Social media best practices document not found in Sanity. Proceeding without this context.")
            social_media_best_practices = ""
    except Exception as e:
        print(f"Warning: Error fetching social media best practices from Sanity: {e}. Proceeding without this context.")
        social_media_best_practices = ""

    # Fetch business context from Sanity
    try:
        query_result = sanity_client.query(
            groq='*[_type == "businessContext"][0]'
        )
        business_context = query_result.get('result')
        if not business_context:
            print("Warning: Business context not found in Sanity. Proceeding without business context.")
            business_context = {}
    except Exception as e:
        print(f"Warning: Error fetching business context from Sanity: {e}. Proceeding without business context.")
        business_context = {}

    notion = notion_client.Client(auth=NOTION_API_KEY)
    
    print("Fetching existing ideas from Notion...")
    existing_ideas = get_existing_notion_ideas(notion, NOTION_DATABASE_ID)
    print(f"Found {len(existing_ideas)} existing ideas.")

    ideas = generate_ideas_with_gemini(content_guidelines, args.num_ideas, args.input_text, existing_ideas, business_context, social_media_best_practices)

    if not ideas:
        print("No ideas were generated. Exiting.")
        return

    print("\nStarting to process new content ideas...")
    for idea in ideas:
        # SAFETY VALIDATION FIRST
        is_safe, safety_issues, safe_alternative = validate_idea_safety(idea)
        
        if not is_safe:
            print(f"🚨 SAFETY ISSUE DETECTED for '{idea.get('title', 'Unknown')}':")
            for issue in safety_issues:
                print(f"   ❌ {issue}")
            print(f"   ✅ Safe alternative: {safe_alternative[:100]}...")
            
            # Replace unsafe content with safe alternative
            idea['body'] = safe_alternative
            idea['title'] = f"SAFE: {idea.get('title', 'Equipment Rental')}"
            print("   🔒 Content replaced with safety-validated version")
        
        # Enhance idea with content pillar classification and smart equipment linking
        enhanced_idea = enhance_idea_quality(idea, business_context)
        
        # Use real equipment images instead of generating new ones
        equipment_images = []
        related_equipment = enhanced_idea.get('related_equipment', [])
        for equipment in related_equipment[:3]:  # Max 3 images
            primary_image = equipment.get('primaryImage')
            if primary_image and primary_image.get('url'):
                equipment_images.append({
                    'url': primary_image['url'],
                    'alt_text': primary_image.get('alt_text', f"Image of {equipment.get('name', 'equipment')}"),
                    'caption': f"{equipment.get('name', 'Equipment')} - {equipment.get('short_description', '')}"
                })
        
        if equipment_images:
            enhanced_idea['equipment_images'] = equipment_images
            print(f"📸 Using {len(equipment_images)} real equipment photos")
        
        sanity_doc_id = save_social_content_to_sanity(enhanced_idea)
        if sanity_doc_id:
            print(f"Idea saved to Sanity with ID: {sanity_doc_id}")
            print(f"Content Pillar: {enhanced_idea.get('content_pillar', 'general_content')}")
            print(f"Equipment Count: {len(enhanced_idea.get('related_equipment', []))}")
            # Add Sanity doc ID to the idea for Notion linking
            enhanced_idea['sanity_doc_id'] = sanity_doc_id
            add_idea_to_notion(notion, enhanced_idea, generate_image_with_gemini, num_images=3)
        else:
            print(f"Failed to save idea to Sanity. Skipping Notion sync for this idea: {enhanced_idea.get('title', 'Unknown Title')}")
    print("Finished processing ideas.")

def classify_content_pillar(idea: dict) -> str:
    """Classify content into specific pillars based on content analysis."""
    title = idea.get('title', '').lower()
    body = idea.get('body', '').lower()
    keywords = idea.get('keywords', '').lower()
    
    combined_text = f"{title} {body} {keywords}"
    
    # Content pillar classification logic
    if any(word in combined_text for word in ['spotlight', 'feature', 'introducing', 'new equipment', 'specs', 'capabilities']):
        return 'equipment_spotlight'
    elif any(word in combined_text for word in ['project', 'showcase', 'customer', 'case study', 'success story']):
        return 'project_showcase'
    elif any(word in combined_text for word in ['construction', 'landscaping', 'agriculture', 'industry', 'commercial']):
        return 'industry_focus'
    elif any(word in combined_text for word in ['winter', 'summer', 'spring', 'fall', 'seasonal', 'weather']):
        return 'seasonal_content'
    elif any(word in combined_text for word in ['safety', 'training', 'certification', 'operator', 'ppe']):
        return 'safety_training'
    elif any(word in combined_text for word in ['maintenance', 'care', 'service', 'repair', 'troubleshoot']):
        return 'maintenance_tips'
    elif any(word in combined_text for word in ['testimonial', 'review', 'before after', 'transformation']):
        return 'customer_success'
    elif any(word in combined_text for word in ['how to', 'guide', 'tips', 'comparison', 'choose']):
        return 'educational_content'
    else:
        return 'general_content'

def get_equipment_by_pillar(pillar: str, idea: dict) -> list:
    """Fetch relevant equipment based on content pillar using optimized GROQ queries."""
    try:
        title = idea.get('title', '').lower()
        body = idea.get('body', '').lower()
        keywords = idea.get('keywords', '').lower()
        
        if pillar == 'equipment_spotlight':
            # Get equipment with rich media and specifications
            query = '''
                *[_type == "equipment" && defined(images)] [0...3] {
                  _id, name, brand, model, short_description, full_description,
                  "primaryImage": images[is_primary == true][0],
                  "firstVideo": video_urls[0], 
                  primary_use_cases, 
                  "dailyRate": pricing.daily_rate,
                  keywords, 
                  "topSpecs": specifications[0...3]
                }
            '''
            
        elif pillar == 'project_showcase':
            # Get equipment for multi-equipment projects (simplified)
            query = '''
                *[_type == "equipment"] [0...4] {
                  _id, name, brand, short_description, 
                  "primaryImage": images[is_primary == true][0],
                  primary_use_cases, 
                  "dailyRate": pricing.daily_rate
                }
            '''
            
        elif pillar == 'industry_focus':
            # Extract industry from content
            industry = 'construction'  # Default
            if 'landscaping' in f"{title} {body} {keywords}":
                industry = 'landscaping'
            elif 'agriculture' in f"{title} {body} {keywords}":
                industry = 'agriculture'
            
            query = f'*[_type == "equipment" && "{industry}" in industries_served[]] [0...3] ' + '''{
                  _id, name, brand, model, short_description, full_description,
                  "primaryImage": images[is_primary == true][0],
                  primary_use_cases, 
                  "dailyRate": pricing.daily_rate,
                  industries_served, project_types,
                  "topSafetyReqs": safety.safety_requirements[0...2]
                }'''
            
        elif pillar == 'seasonal_content':
            # Get weather-appropriate equipment
            season = 'winter' if any(word in f"{title} {body} {keywords}" for word in ['winter', 'snow', 'cold']) else 'summer'
            
            query = f'*[_type == "equipment" && ("{season}" in keywords[] || "outdoor" in primary_use_cases[] || "all-season" in keywords[])] [0...3] ' + '''{
                  _id, name, brand, short_description,
                  "primaryImage": images[is_primary == true][0],
                  "weatherSpecs": specifications[name match "*temperature*" || name match "*weather*"],
                  primary_use_cases, 
                  "protectiveEquipment": safety.protective_equipment_required
                }'''
            
        elif pillar == 'safety_training':
            # Get equipment with safety requirements
            query = '''
                *[_type == "equipment" && 
                  (safety.operator_certification_required == true || 
                   count(safety.safety_requirements) > 0)] [0...3] {
                  _id, name, brand, short_description,
                  "primaryImage": images[is_primary == true][0],
                  "safetyRequirements": safety.safety_requirements, 
                  "certificationRequired": safety.operator_certification_required,
                  "protectiveEquipment": safety.protective_equipment_required, 
                  manual_urls
                }
            '''
            
        else:
            # Default query for general content
            query = '''
                *[_type == "equipment"] [0...2] {
                  _id, name, brand, short_description,
                  "primaryImage": images[is_primary == true][0],
                  primary_use_cases, 
                  "dailyRate": pricing.daily_rate
                }
            '''
        
        # Execute GROQ query
        result = sanity_client.query(query)
        equipment_data = result.get('result', [])
        
        return equipment_data
        
    except Exception as e:
        logger.error(f"Error fetching equipment for pillar {pillar}: {e}")
        return []

def enhance_idea_quality(idea: dict, business_context: dict) -> dict:
    """Enhance the generated idea with content pillar classification and smart equipment linking."""
    enhanced = idea.copy()
    
    # Classify content pillar
    pillar = classify_content_pillar(idea)
    enhanced['content_pillar'] = pillar
    
    # Determine platform based on content characteristics
    body = idea.get('body', '').lower()
    if any(word in body for word in ['video', 'watch', 'check out this']):
        enhanced['platform'] = 'Instagram/TikTok'
    elif any(word in body for word in ['#', 'hashtag', 'follow']):
        enhanced['platform'] = 'Instagram'
    elif len(body) > 200:
        enhanced['platform'] = 'Facebook'
    else:
        enhanced['platform'] = 'Multi-platform'
    
    # Get relevant equipment using pillar-specific queries
    equipment_data = get_equipment_by_pillar(pillar, idea)
    enhanced['related_equipment'] = equipment_data
    
    # Add equipment insights for content generation
    if equipment_data:
        enhanced['equipment_insights'] = {
            'total_equipment': len(equipment_data),
            'featured_equipment': equipment_data[0].get('name', '') if equipment_data else '',
            'price_range': {
                'min': min([eq.get('pricing', {}).get('daily_rate', 0) for eq in equipment_data if eq.get('pricing', {}).get('daily_rate')], default=0),
                'max': max([eq.get('pricing', {}).get('daily_rate', 0) for eq in equipment_data if eq.get('pricing', {}).get('daily_rate')], default=0)
            } if any(eq.get('pricing', {}).get('daily_rate') for eq in equipment_data) else None,
            'safety_required': any(eq.get('safety', {}).get('operator_certification_required') for eq in equipment_data),
            'industries': list(set([industry for eq in equipment_data for industry in eq.get('industries_served', [])]))
        }
    
    return enhanced


if __name__ == "__main__":
    main()