#!/usr/bin/env python3
"""
Enhanced Image Generation with Gemini 2.0 Image Editing
Implements intelligent image enhancement using equipment photos and AI editing.
"""

import os
import logging
import asyncio
import aiohttp
from typing import List, Dict, Any, Optional, Tuple
from io import BytesIO
from PIL import Image
import base64

from google import genai
from google.genai import types

from .config_loader import ConfigurationLoader

logger = logging.getLogger(__name__)

class EnhancedImageGenerator:
    """Enhanced image generation with Gemini 2.0 image editing"""
    
    def __init__(self, config_loader: ConfigurationLoader, gemini_api_key: str):
        self.config = config_loader
        self.gemini_client = genai.Client(api_key=gemini_api_key)
        
    async def enhance_equipment_images(self, 
                                     equipment_data: List[Dict], 
                                     content_pillar: str,
                                     platform: str,
                                     content_context: str) -> List[Dict[str, Any]]:
        """Enhance equipment images based on content pillar and context"""
        
        logger.info(f"Enhancing {len(equipment_data)} equipment images for {content_pillar}")
        
        enhanced_images = []
        max_images = self.config.image_config.generation_rules.get('maxImagesPerPost', 3)
        
        # Process up to max_images equipment items
        for i, equipment in enumerate(equipment_data[:max_images]):
            try:
                # Get original equipment image
                original_image_url = self._get_equipment_image_url(equipment)
                if not original_image_url:
                    logger.warning(f"No image found for equipment: {equipment.get('name', 'Unknown')}")
                    continue
                
                # Download original image
                image_data = await self._download_image(original_image_url)
                if not image_data:
                    logger.warning(f"Failed to download image for: {equipment.get('name', 'Unknown')}")
                    continue
                
                # Generate enhancement prompt
                enhancement_prompt = self._generate_enhancement_prompt(
                    content_pillar, equipment, content_context, platform
                )
                
                # Enhance image with Gemini 2.0
                enhanced_image = await self._enhance_image_with_gemini(
                    image_data, enhancement_prompt, equipment
                )
                
                if enhanced_image:
                    enhanced_images.append(enhanced_image)
                    logger.info(f"✅ Enhanced image for: {equipment.get('name', 'Unknown')}")
                else:
                    # Fallback to original image
                    fallback_image = self._create_fallback_image_entry(equipment, original_image_url)
                    enhanced_images.append(fallback_image)
                    logger.info(f"⚠️  Used original image for: {equipment.get('name', 'Unknown')}")
                
            except Exception as e:
                logger.error(f"Error enhancing image for {equipment.get('name', 'Unknown')}: {e}")
                # Create fallback entry
                if 'original_image_url' in locals():
                    fallback_image = self._create_fallback_image_entry(equipment, original_image_url)
                    enhanced_images.append(fallback_image)
        
        logger.info(f"Successfully processed {len(enhanced_images)} images")
        return enhanced_images
    
    def _get_equipment_image_url(self, equipment: Dict) -> Optional[str]:
        """Extract image URL from equipment data"""
        try:
            # Check for primary image
            primary_image = equipment.get('primaryImage')
            if primary_image and primary_image.get('url'):
                return primary_image['url']
            
            # Check for first image in images array
            images = equipment.get('images', [])
            if images and len(images) > 0:
                first_image = images[0]
                if isinstance(first_image, dict) and first_image.get('url'):
                    return first_image['url']
                elif isinstance(first_image, str):
                    return first_image
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting image URL: {e}")
            return None
    
    async def _download_image(self, image_url: str) -> Optional[bytes]:
        """Download image from URL"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url, timeout=30) as response:
                    if response.status == 200:
                        return await response.read()
                    else:
                        logger.error(f"Failed to download image: HTTP {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error downloading image from {image_url}: {e}")
            return None
    
    def _generate_enhancement_prompt(self, 
                                   content_pillar: str, 
                                   equipment: Dict, 
                                   content_context: str,
                                   platform: str) -> str:
        """Generate context-aware enhancement prompt"""
        
        # Get base enhancement prompt for pillar
        base_prompt = self.config.image_config.enhancement_prompts.get(
            content_pillar, 
            "Enhance this equipment image with professional lighting and clean background."
        )
        
        # Get equipment details
        equipment_name = equipment.get('name', 'equipment')
        equipment_description = equipment.get('short_description', '')
        
        # Get brand guidelines
        brand_guidelines = self.config.image_config.brand_guidelines
        visual_style = brand_guidelines.get('visualStyle', 'professional')
        brand_colors = brand_guidelines.get('brandColors', [])
        
        # Build contextual prompt
        prompt_parts = [base_prompt]
        
        # Add equipment-specific context
        if equipment_description:
            prompt_parts.append(f"This is a {equipment_name}: {equipment_description}.")
        
        # Add content context
        if content_context:
            prompt_parts.append(f"Content context: {content_context}.")
        
        # Add platform-specific optimization
        platform_specs = self._get_platform_image_specs(platform)
        if platform_specs:
            aspect_ratio = platform_specs.get('aspectRatio', '1:1')
            prompt_parts.append(f"Optimize for {platform} with {aspect_ratio} aspect ratio.")
        
        # Add brand guidelines
        prompt_parts.append(f"Maintain {visual_style} visual style.")
        
        if brand_colors:
            color_names = [color.get('name', 'brand color') for color in brand_colors[:2]]
            prompt_parts.append(f"Incorporate brand colors: {', '.join(color_names)}.")
        
        # Add safety requirements
        safety_filters = self.config.image_config.safety_filters
        if safety_filters.get('requiredSafetyElements'):
            safety_elements = safety_filters['requiredSafetyElements'][:2]  # Top 2
            prompt_parts.append(f"Ensure safety elements are visible: {', '.join(safety_elements)}.")
        
        # Add watermark instruction
        generation_rules = self.config.image_config.generation_rules
        if generation_rules.get('includeWatermark', True):
            watermark_position = generation_rules.get('watermarkPosition', 'bottom-right')
            prompt_parts.append(f"Add Rental Village watermark in {watermark_position} corner.")
        
        return " ".join(prompt_parts)
    
    def _get_platform_image_specs(self, platform: str) -> Optional[Dict]:
        """Get platform-specific image specifications"""
        try:
            platform_config = getattr(self.config.platform_config, platform.lower(), None)
            if platform_config:
                return platform_config.get('imageSpecs', {})
            return None
        except Exception as e:
            logger.error(f"Error getting platform specs for {platform}: {e}")
            return None
    
    async def _enhance_image_with_gemini(self, 
                                       image_data: bytes, 
                                       enhancement_prompt: str,
                                       equipment: Dict) -> Optional[Dict[str, Any]]:
        """Enhance image using Gemini 2.0 image generation"""
        
        try:
            # Convert image data to PIL Image
            pil_image = Image.open(BytesIO(image_data))
            
            # Prepare input for Gemini
            text_input = enhancement_prompt
            
            logger.debug(f"Enhancing image with prompt: {enhancement_prompt[:100]}...")
            
            # Call Gemini 2.0 image generation
            response = self.gemini_client.models.generate_content(
                model="gemini-2.0-flash-preview-image-generation",
                contents=[text_input, pil_image],
                config=types.GenerateContentConfig(
                    response_modalities=['TEXT', 'IMAGE']
                )
            )
            
            # Process response
            enhanced_image_data = None
            response_text = ""
            
            for part in response.candidates[0].content.parts:
                if part.text is not None:
                    response_text = part.text
                elif part.inline_data is not None:
                    enhanced_image_data = part.inline_data.data
            
            if enhanced_image_data:
                # Create enhanced image entry
                enhanced_image = {
                    'type': 'enhanced',
                    'equipment_name': equipment.get('name', 'Unknown'),
                    'equipment_id': equipment.get('_id'),
                    'image_data': enhanced_image_data,
                    'enhancement_description': response_text,
                    'enhancement_prompt': enhancement_prompt,
                    'alt_text': f"Enhanced image of {equipment.get('name', 'equipment')}",
                    'caption': f"{equipment.get('name', 'Equipment')} - {equipment.get('short_description', 'Professional rental equipment')}"
                }
                
                return enhanced_image
            
            else:
                logger.warning("No enhanced image data received from Gemini")
                return None
                
        except Exception as e:
            logger.error(f"Error enhancing image with Gemini: {e}")
            return None
    
    def _create_fallback_image_entry(self, equipment: Dict, original_url: str) -> Dict[str, Any]:
        """Create fallback image entry using original equipment photo"""
        
        return {
            'type': 'original',
            'equipment_name': equipment.get('name', 'Unknown'),
            'equipment_id': equipment.get('_id'),
            'url': original_url,
            'enhancement_description': 'Using original equipment photo',
            'alt_text': f"Image of {equipment.get('name', 'equipment')}",
            'caption': f"{equipment.get('name', 'Equipment')} - {equipment.get('short_description', 'Professional rental equipment')}"
        }
    
    def validate_enhanced_images(self, images: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate enhanced images meet quality standards"""
        
        validated_images = []
        quality_standards = self.config.image_config.quality_standards
        
        for image in images:
            try:
                # Basic validation
                if not image:
                    continue
                
                # Check if we have image data or URL
                has_image = (
                    image.get('image_data') or 
                    image.get('url') or 
                    image.get('original_url')
                )
                
                if not has_image:
                    logger.warning(f"Image validation failed: No image data for {image.get('equipment_name', 'Unknown')}")
                    continue
                
                # Validate caption and alt text
                if not image.get('alt_text'):
                    image['alt_text'] = f"Image of {image.get('equipment_name', 'equipment')}"
                
                if not image.get('caption'):
                    image['caption'] = f"{image.get('equipment_name', 'Equipment')} available for rent"
                
                # Apply safety filters if available
                safety_filters = self.config.image_config.safety_filters
                if safety_filters.get('automaticSafetyCheck', True):
                    # In a full implementation, this would use image analysis to check for safety violations
                    # For now, we'll assume images pass safety checks
                    pass
                
                validated_images.append(image)
                
            except Exception as e:
                logger.error(f"Error validating image {image.get('equipment_name', 'Unknown')}: {e}")
                continue
        
        logger.info(f"Validated {len(validated_images)} out of {len(images)} images")
        return validated_images
    
    async def optimize_for_platform(self, 
                                   images: List[Dict[str, Any]], 
                                   platform: str) -> List[Dict[str, Any]]:
        """Optimize images for specific platform requirements"""
        
        try:
            platform_specs = self._get_platform_image_specs(platform)
            if not platform_specs:
                logger.warning(f"No platform specs found for {platform}")
                return images
            
            optimized_images = []
            target_width = platform_specs.get('width', 1080)
            target_height = platform_specs.get('height', 1080)
            
            for image in images:
                # For enhanced images with data, we would resize them here
                # For original images with URLs, we keep them as-is but add platform metadata
                
                optimized_image = image.copy()
                optimized_image['platform_optimized'] = platform
                optimized_image['target_dimensions'] = {
                    'width': target_width,
                    'height': target_height
                }
                
                optimized_images.append(optimized_image)
            
            return optimized_images
            
        except Exception as e:
            logger.error(f"Error optimizing images for {platform}: {e}")
            return images
    
    def get_generation_summary(self, images: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get summary of image generation results"""
        
        total_images = len(images)
        enhanced_count = len([img for img in images if img.get('type') == 'enhanced'])
        original_count = len([img for img in images if img.get('type') == 'original'])
        
        equipment_names = [img.get('equipment_name', 'Unknown') for img in images]
        
        return {
            'total_images': total_images,
            'enhanced_images': enhanced_count,
            'original_images': original_count,
            'enhancement_rate': enhanced_count / total_images if total_images > 0 else 0,
            'equipment_featured': equipment_names,
            'success': total_images > 0
        }