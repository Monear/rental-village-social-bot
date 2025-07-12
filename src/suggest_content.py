#!/usr/bin/env python3
"""
Suggest Content - Strategic Content Generation System
Advanced social media content generation with strategic planning, equipment targeting,
parallel processing, and Gemini 2.0 image enhancement.
"""

import os
import sys
import argparse
import asyncio
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Enhanced imports
from src.utils.config_loader import ConfigurationLoader
from src.utils.content_strategy_engine import ContentStrategyEngine
from src.utils.enhanced_image_generation import EnhancedImageGenerator

# Original imports
from src.utils.general import read_file_content
from src.utils.gemini_helpers import generate_ideas_with_gemini, generate_image_with_gemini
from src.utils.notion_helpers import add_idea_to_notion, get_existing_notion_ideas
from src.utils.sanity_helpers import save_social_content_to_sanity
from src.utils.safety_validator import validate_idea_safety

import notion_client
import json
from sanity import Client

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'), override=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
NOTION_API_KEY = os.getenv("NOTION_TOKEN")
NOTION_DATABASE_ID = os.getenv("DATABASE_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SANITY_PROJECT_ID = os.environ.get("SANITY_PROJECT_ID", "2pxuaj9k")
SANITY_DATASET = os.environ.get("SANITY_DATASET", "production")
SANITY_API_TOKEN = os.environ.get("SANITY_API_TOKEN")

# Initialize clients
sanity_client = Client(
    project_id=SANITY_PROJECT_ID,
    dataset=SANITY_DATASET,
    token=SANITY_API_TOKEN,
    use_cdn=False,  # Disable CDN to get fresh data
    logger=logger
)

class ContentGenerator:
    """Strategic content generation system with advanced planning and targeting"""
    
    def __init__(self):
        self.config_loader = ConfigurationLoader(sanity_client)
        self.strategy_engine = None
        self.image_generator = None
        self.notion_client = None
        
    async def initialize(self):
        """Initialize all components"""
        logger.info("🚀 Initializing Strategic Content Generation System...")
        
        # Load configurations
        if not self.config_loader.load_all_configurations():
            raise ValueError("Failed to load system configurations")
        
        # Initialize strategy engine
        self.strategy_engine = ContentStrategyEngine(self.config_loader, sanity_client)
        
        # Initialize image generator
        self.image_generator = EnhancedImageGenerator(self.config_loader, GEMINI_API_KEY)
        
        # Initialize Notion client
        self.notion_client = notion_client.Client(auth=NOTION_API_KEY)
        
        logger.info("✅ System initialized successfully")
    
    async def generate_strategic_content(self, num_ideas: int = 1) -> list:
        """Generate content using strategic planning approach"""
        
        logger.info(f"🎯 Starting strategic content generation for {num_ideas} ideas...")
        
        # Step 1: Strategic Content Planning
        logger.info("📋 Step 1: Strategic Content Planning")
        content_plans = self.strategy_engine.plan_strategic_content(num_ideas)
        
        # Step 2: Fetch existing content for duplication check
        logger.info("🔍 Step 2: Fetching existing content")
        existing_ideas = get_existing_notion_ideas(self.notion_client, NOTION_DATABASE_ID)
        logger.info(f"Found {len(existing_ideas)} existing ideas for duplication check")
        
        # Step 3: Process each content plan
        generated_content = []
        
        for i, plan in enumerate(content_plans, 1):
            logger.info(f"\n🎨 Processing Content Plan {i}/{len(content_plans)}")
            logger.info(f"   Pillar: {plan.pillar}")
            logger.info(f"   Platform: {plan.target_platform}")
            logger.info(f"   Equipment Category: {plan.equipment_category}")
            logger.info(f"   Priority Score: {plan.priority_score:.2f}")
            logger.info(f"   Rationale: {plan.business_rationale}")
            
            try:
                # Generate content based on plan
                content = await self._process_content_plan(plan, existing_ideas)
                if content:
                    generated_content.append(content)
                    logger.info(f"✅ Successfully generated content: {content.get('title', 'Untitled')}")
                else:
                    logger.warning(f"⚠️  Failed to generate content for plan {i}")
                    
            except Exception as e:
                logger.error(f"❌ Error processing plan {i}: {e}")
                continue
        
        logger.info(f"\n🎉 Strategic content generation complete!")
        logger.info(f"Generated {len(generated_content)} out of {num_ideas} requested ideas")
        
        return generated_content
    
    async def _process_content_plan(self, plan, existing_ideas: list) -> dict:
        """Process individual content plan with parallel execution"""
        
        # Step 3a: Get strategic equipment targeting
        logger.info("🎯 Step 3a: Strategic Equipment Targeting")
        equipment_target = self.strategy_engine.get_equipment_targets(plan)
        
        if not equipment_target.specific_equipment_ids:
            logger.warning(f"No equipment found for category: {plan.equipment_category}")
            return None
        
        logger.info(f"   Found {len(equipment_target.specific_equipment_ids)} target equipment items")
        logger.info(f"   Priority reasons: {', '.join(equipment_target.priority_reasons)}")
        
        # Step 3b: Fetch equipment data
        logger.info("📦 Step 3b: Fetching Equipment Data")
        equipment_data = await self._fetch_equipment_data(equipment_target.specific_equipment_ids)
        
        if not equipment_data:
            logger.warning("No equipment data retrieved")
            return None
        
        # Step 3c: Prepare content generation context
        logger.info("📝 Step 3c: Preparing Content Context")
        content_context = self._build_content_context(plan, equipment_data)
        
        # Step 3d: Parallel Content Generation
        logger.info("⚡ Step 3d: Parallel Content & Image Processing")
        
        # Generate content text first
        logger.info("   🤖 Generating content text...")
        content_text = self._generate_content_text(plan, content_context, existing_ideas)
        
        # Try image generation, but continue without it if there are API issues
        logger.info("   🎨 Attempting image generation...")
        try:
            enhanced_images = await self.image_generator.enhance_equipment_images(
                equipment_data, plan.pillar, plan.target_platform, content_context.get('themes', '')
            )
            logger.info(f"   ✅ Generated {len(enhanced_images)} enhanced images")
        except Exception as e:
            logger.warning(f"   ⚠️  Image generation failed: {e}")
            logger.info("   📝 Continuing without images - you can use Canva for final post images")
            enhanced_images = []
        
        if not content_text:
            logger.error("Failed to generate content text")
            return None
        
        # Step 3e: Safety Validation
        logger.info("🔒 Step 3e: Safety Validation")
        is_safe, safety_issues, safe_alternative = validate_idea_safety(content_text)
        
        if not is_safe:
            logger.warning(f"🚨 Safety issues detected: {', '.join(safety_issues)}")
            content_text['body'] = safe_alternative
            content_text['title'] = f"SAFE: {content_text.get('title', 'Equipment Rental')}"
            logger.info("   🔒 Content replaced with safety-validated version")
        
        # Step 3f: Platform Optimization
        logger.info("📱 Step 3f: Platform Optimization")
        optimized_content = await self._optimize_for_platform(
            content_text, enhanced_images, plan.target_platform
        )
        
        # Step 3g: Final Assembly
        logger.info("🔧 Step 3g: Final Content Assembly")
        final_content = self._assemble_final_content(
            optimized_content, enhanced_images, equipment_data, plan
        )
        
        return final_content
    
    async def _fetch_equipment_data(self, equipment_ids: list) -> list:
        """Fetch comprehensive equipment data"""
        try:
            if not equipment_ids:
                return []
            
            # Build query for specific equipment IDs
            id_filter = ' || '.join([f'_id == "{eid}"' for eid in equipment_ids])
            
            query = f'''*[_type == "equipment" && ({id_filter})] {{
                _id, name, brand, model, short_description, full_description,
                "primaryImage": images[is_primary == true][0],
                images, video_urls, primary_use_cases,
                "dailyRate": pricing.daily_rate,
                categories, industries_served, project_types,
                specifications, safety, keywords, popularity_score
            }}'''
            
            result = sanity_client.query(query)
            equipment_data = result.get('result', [])
            
            logger.info(f"   Retrieved data for {len(equipment_data)} equipment items")
            return equipment_data
            
        except Exception as e:
            logger.error(f"Error fetching equipment data: {e}")
            return []
    
    def _build_content_context(self, plan, equipment_data: list) -> dict:
        """Build comprehensive content context"""
        
        # Get seasonal context
        seasonal_config = self.config_loader.seasonal_config
        current_season = seasonal_config.current_season
        seasonal_themes = seasonal_config.seasonal_content_themes.get(current_season, [])
        seasonal_keywords = seasonal_config.seasonal_keywords.get(current_season, [])
        
        # Extract equipment insights
        equipment_names = [eq.get('name', '') for eq in equipment_data]
        equipment_uses = []
        for eq in equipment_data:
            uses = eq.get('primary_use_cases', [])
            equipment_uses.extend(uses)
        
        # Get platform preferences
        platform_config = getattr(self.config_loader.platform_config, plan.target_platform.lower(), {})
        
        context = {
            'pillar': plan.pillar,
            'platform': plan.target_platform,
            'equipment_category': plan.equipment_category,
            'season': current_season,
            'themes': seasonal_themes,
            'seasonal_keywords': seasonal_keywords,
            'equipment_names': equipment_names,
            'equipment_uses': equipment_uses,
            'business_rationale': plan.business_rationale,
            'platform_config': platform_config,
            'priority_score': plan.priority_score
        }
        
        return context
    
    def _generate_content_text(self, plan, content_context: dict, existing_ideas: list) -> dict:
        """Generate content text using existing Gemini helpers with retry logic"""
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                logger.info(f"   🤖 Generating content text with Gemini (attempt {attempt + 1}/{max_retries})...")
                
                # Build enhanced prompt based on strategic context
                enhanced_prompt = self._build_strategic_prompt(plan, content_context)
                
                # Get content guidelines and business context
                content_guidelines_result = sanity_client.query(
                    '*[_type == "contentPrompt" && title == "Content Generation Prompt"][0]'
                )
                content_guidelines = content_guidelines_result.get('result', {}).get('content', '')
                
                business_context_result = sanity_client.query('*[_type == "businessContext"][0]')
                business_context = business_context_result.get('result', {})
                
                social_media_best_practices_result = sanity_client.query(
                    '*[_type == "contentPrompt" && title == "Social Media Best Practices"][0]'
                )
                social_media_best_practices = social_media_best_practices_result.get('result', {}).get('content', '')
                
                # Generate content using existing function with enhanced context
                ideas = generate_ideas_with_gemini(
                    guidelines=f"{content_guidelines}\n\nSTRATEGIC CONTEXT:\n{enhanced_prompt}",
                    num_ideas=1,
                    user_input=None,
                    existing_ideas=existing_ideas,
                    machine_context=business_context,
                    social_media_best_practices=social_media_best_practices
                )
                
                if ideas and len(ideas) > 0:
                    content = ideas[0]
                    # Add strategic metadata
                    content['pillar'] = plan.pillar  # Use 'pillar' for Notion compatibility
                    content['content_pillar'] = plan.pillar
                    content['target_platform'] = plan.target_platform
                    content['equipment_category'] = plan.equipment_category
                    content['priority_score'] = plan.priority_score
                    content['generation_method'] = 'strategic_planning'
                    
                    logger.info("   ✅ Content generation successful!")
                    return content
                
                logger.warning(f"   ⚠️  No ideas generated on attempt {attempt + 1}")
                
            except Exception as e:
                error_msg = str(e)
                logger.warning(f"   ⚠️  Content generation attempt {attempt + 1} failed: {error_msg}")
                
                # Check if it's a 503 error (API overloaded)
                if "503" in error_msg or "overloaded" in error_msg.lower():
                    if attempt < max_retries - 1:
                        logger.info(f"   ⏳ API overloaded, waiting {retry_delay} seconds before retry...")
                        import time
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                        continue
                    else:
                        logger.error("   ❌ All retry attempts failed due to API overload")
                else:
                    logger.error(f"   ❌ Non-retryable error: {error_msg}")
                    break
        
        logger.error("   ❌ Content generation failed after all attempts")
        return None
    
    def _build_strategic_prompt(self, plan, content_context: dict) -> str:
        """Build strategic prompt for content generation"""
        
        prompt_parts = [
            f"Content Pillar: {plan.pillar}",
            f"Target Platform: {plan.target_platform}",
            f"Equipment Focus: {plan.equipment_category}",
            f"Seasonal Context: {content_context.get('season', 'current')} season"
        ]
        
        if content_context.get('equipment_names'):
            prompt_parts.append(f"Featured Equipment: {', '.join(content_context['equipment_names'][:3])}")
        
        if content_context.get('themes'):
            prompt_parts.append(f"Seasonal Themes: {', '.join(content_context['themes'][:2])}")
        
        if content_context.get('equipment_uses'):
            prompt_parts.append(f"Equipment Applications: {', '.join(content_context['equipment_uses'][:3])}")
        
        prompt_parts.append(f"Business Rationale: {plan.business_rationale}")
        
        # Add platform-specific guidance
        platform_config = content_context.get('platform_config', {})
        if platform_config:
            content_style = platform_config.get('contentStyle', {})
            if content_style.get('tone'):
                prompt_parts.append(f"Content Tone: {content_style['tone']}")
            
            content_length = platform_config.get('contentLength', {})
            if content_length.get('optimal'):
                prompt_parts.append(f"Target Length: ~{content_length['optimal']} characters")
        
        return "\n".join(prompt_parts)
    
    
    async def _optimize_for_platform(self, content_text: dict, enhanced_images: list, platform: str) -> dict:
        """Optimize content for specific platform"""
        try:
            logger.info(f"   📱 Optimizing content for {platform}...")
            
            # Get platform configuration
            platform_config = getattr(self.config_loader.platform_config, platform.lower(), {})
            
            optimized_content = content_text.copy()
            
            # Apply platform-specific optimizations
            if platform_config:
                content_length_config = platform_config.get('contentLength', {})
                max_length = content_length_config.get('max', 2000)
                
                # Truncate if necessary
                current_body = optimized_content.get('body', '')
                if len(current_body) > max_length:
                    optimized_content['body'] = current_body[:max_length-3] + "..."
                    logger.info(f"   ✂️  Truncated content to {max_length} characters")
                
                # Add platform-specific metadata
                optimized_content['platform_optimized'] = platform
                optimized_content['platform_specs'] = platform_config
            
            # Optimize images for platform
            if enhanced_images:
                optimized_images = await self.image_generator.optimize_for_platform(
                    enhanced_images, platform
                )
                optimized_content['optimized_images'] = optimized_images
            
            return optimized_content
            
        except Exception as e:
            logger.error(f"Error optimizing for platform {platform}: {e}")
            return content_text
    
    def _assemble_final_content(self, content: dict, images: list, equipment_data: list, plan) -> dict:
        """Assemble final content with all components"""
        
        final_content = content.copy()
        
        # Add equipment data
        final_content['related_equipment'] = equipment_data
        final_content['equipment_count'] = len(equipment_data)
        
        # Add enhanced images (sanitized for JSON serialization)
        if images:
            # Create clean version without binary data for JSON serialization
            sanitized_images = []
            for img in images:
                clean_img = {
                    'type': img.get('type'),
                    'equipment_name': img.get('equipment_name'),
                    'equipment_id': img.get('equipment_id'),
                    'enhancement_description': img.get('enhancement_description'),
                    'alt_text': img.get('alt_text'),
                    'caption': img.get('caption'),
                    'url': img.get('url')  # Only include URL if present, not binary data
                }
                # Remove None values
                clean_img = {k: v for k, v in clean_img.items() if v is not None}
                sanitized_images.append(clean_img)
            
            final_content['enhanced_images'] = images  # Keep full data for Notion/processing
            final_content['enhanced_images_clean'] = sanitized_images  # Clean version for JSON
            final_content['image_count'] = len(images)
            
            # Get generation summary
            image_summary = self.image_generator.get_generation_summary(images)
            final_content['image_generation_summary'] = image_summary
        
        # Add strategic metadata
        final_content.update({
            'content_pillar': plan.pillar,
            'target_platform': plan.target_platform,
            'equipment_category': plan.equipment_category,
            'seasonal_context': plan.seasonal_context,
            'priority_score': plan.priority_score,
            'business_rationale': plan.business_rationale,
            'generation_timestamp': datetime.now().isoformat(),
            'generation_method': 'strategic_planning'
        })
        
        return final_content

async def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="Strategic content generation with advanced planning")
    parser.add_argument("--num-ideas", type=int, default=2, help="Number of content ideas to generate")
    parser.add_argument("--analyze-performance", action="store_true", help="Analyze content performance")
    args = parser.parse_args()
    
    # Validate environment
    if not all([NOTION_API_KEY, NOTION_DATABASE_ID, GEMINI_API_KEY, SANITY_API_TOKEN]):
        logger.error("❌ Required API keys not found. Check your .env file.")
        return
    
    try:
        # Initialize content generator
        generator = ContentGenerator()
        await generator.initialize()
        
        # Optional: Analyze performance first
        if args.analyze_performance:
            logger.info("📊 Analyzing content performance...")
            analysis = generator.strategy_engine.analyze_content_performance()
            logger.info(f"Performance Analysis: {json.dumps(analysis, indent=2)}")
        
        # Generate strategic content
        generated_content = await generator.generate_strategic_content(args.num_ideas)
        
        if not generated_content:
            logger.error("❌ No content was generated")
            return
        
        # Save and sync content
        logger.info("\n💾 Saving and syncing content...")
        
        for i, content in enumerate(generated_content, 1):
            try:
                # Save to Sanity
                sanity_doc_id = save_social_content_to_sanity(content)
                if sanity_doc_id:
                    logger.info(f"✅ Content {i} saved to Sanity: {sanity_doc_id}")
                    content['sanity_doc_id'] = sanity_doc_id
                    
                    # Add to Notion
                    add_idea_to_notion(
                        generator.notion_client, 
                        content, 
                        generate_image_with_gemini, 
                        num_images=len(content.get('enhanced_images', []))
                    )
                    logger.info(f"✅ Content {i} added to Notion")
                    
                else:
                    logger.error(f"❌ Failed to save content {i} to Sanity")
                    
            except Exception as e:
                logger.error(f"❌ Error saving content {i}: {e}")
        
        logger.info("\n🎉 Strategic content generation completed successfully!")
        logger.info(f"Generated and saved {len(generated_content)} strategic content ideas")
        
    except Exception as e:
        logger.error(f"❌ Strategic content generation failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())