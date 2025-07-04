#!/usr/bin/env python3
"""
Configuration Loader for Enhanced Content Strategy System
Loads all configuration data from Sanity for strategic content generation.
"""

import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from sanity import Client

logger = logging.getLogger(__name__)

@dataclass
class ContentStrategyConfig:
    """Content strategy configuration from Sanity"""
    pillar_weights: Dict[str, float]
    platform_preferences: Dict[str, int]
    equipment_selection_rules: Dict[str, Any]
    content_quality_rules: Dict[str, Any]

@dataclass
class SeasonalConfig:
    """Seasonal settings configuration from Sanity"""
    current_season: str
    seasonal_keywords: Dict[str, list]
    seasonal_equipment_priority: Dict[str, list]
    seasonal_content_themes: Dict[str, list]
    seasonal_boosts: Dict[str, float]
    weather_considerations: Dict[str, Any]

@dataclass
class ImageGenerationConfig:
    """Image generation settings from Sanity"""
    brand_guidelines: Dict[str, Any]
    enhancement_prompts: Dict[str, str]
    quality_standards: Dict[str, Any]
    generation_rules: Dict[str, Any]
    safety_filters: Dict[str, Any]

@dataclass
class PlatformConfig:
    """Platform-specific settings from Sanity"""
    facebook: Dict[str, Any]
    instagram: Dict[str, Any]
    blog: Dict[str, Any]
    cross_platform_settings: Dict[str, Any]

class ConfigurationLoader:
    """Loads and manages all configuration data from Sanity"""
    
    def __init__(self, sanity_client: Client):
        self.sanity_client = sanity_client
        self._content_strategy: Optional[ContentStrategyConfig] = None
        self._seasonal_config: Optional[SeasonalConfig] = None
        self._image_config: Optional[ImageGenerationConfig] = None
        self._platform_config: Optional[PlatformConfig] = None
        
    def load_all_configurations(self) -> bool:
        """Load all configuration data from Sanity"""
        try:
            logger.info("Loading all configuration data from Sanity...")
            
            # Load content strategy
            self._content_strategy = self._load_content_strategy()
            if not self._content_strategy:
                logger.error("Failed to load content strategy configuration")
                return False
            
            # Load seasonal settings
            self._seasonal_config = self._load_seasonal_config()
            if not self._seasonal_config:
                logger.error("Failed to load seasonal configuration")
                return False
            
            # Load image generation settings
            self._image_config = self._load_image_config()
            if not self._image_config:
                logger.error("Failed to load image generation configuration")
                return False
            
            # Load platform settings
            self._platform_config = self._load_platform_config()
            if not self._platform_config:
                logger.error("Failed to load platform configuration")
                return False
            
            logger.info("✅ All configurations loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading configurations: {e}")
            return False
    
    def _load_content_strategy(self) -> Optional[ContentStrategyConfig]:
        """Load content strategy configuration"""
        try:
            result = self.sanity_client.query(
                '*[_type == "contentStrategy" && active == true][0]'
            )
            
            config_data = result.get('result')
            if not config_data:
                logger.warning("No active content strategy found")
                return None
            
            return ContentStrategyConfig(
                pillar_weights=config_data.get('pillarWeights', {}),
                platform_preferences=config_data.get('platformPreferences', {}),
                equipment_selection_rules=config_data.get('equipmentSelectionRules', {}),
                content_quality_rules=config_data.get('contentQualityRules', {})
            )
            
        except Exception as e:
            logger.error(f"Error loading content strategy: {e}")
            return None
    
    def _load_seasonal_config(self) -> Optional[SeasonalConfig]:
        """Load seasonal settings configuration"""
        try:
            result = self.sanity_client.query(
                '*[_type == "seasonalSettings" && active == true][0]'
            )
            
            config_data = result.get('result')
            if not config_data:
                logger.warning("No active seasonal settings found")
                return None
            
            return SeasonalConfig(
                current_season=config_data.get('currentSeason', 'winter'),
                seasonal_keywords=config_data.get('seasonalKeywords', {}),
                seasonal_equipment_priority=config_data.get('seasonalEquipmentPriority', {}),
                seasonal_content_themes=config_data.get('seasonalContentThemes', {}),
                seasonal_boosts=config_data.get('seasonalBoosts', {}),
                weather_considerations=config_data.get('weatherConsiderations', {})
            )
            
        except Exception as e:
            logger.error(f"Error loading seasonal config: {e}")
            return None
    
    def _load_image_config(self) -> Optional[ImageGenerationConfig]:
        """Load image generation settings"""
        try:
            result = self.sanity_client.query(
                '*[_type == "imageGenerationSettings" && active == true][0]'
            )
            
            config_data = result.get('result')
            if not config_data:
                logger.warning("No active image generation settings found")
                return None
            
            return ImageGenerationConfig(
                brand_guidelines=config_data.get('brandGuidelines', {}),
                enhancement_prompts=config_data.get('imageEnhancementPrompts', {}),
                quality_standards=config_data.get('imageQualityStandards', {}),
                generation_rules=config_data.get('generationRules', {}),
                safety_filters=config_data.get('safetyFilters', {})
            )
            
        except Exception as e:
            logger.error(f"Error loading image config: {e}")
            return None
    
    def _load_platform_config(self) -> Optional[PlatformConfig]:
        """Load platform-specific settings"""
        try:
            result = self.sanity_client.query(
                '*[_type == "platformSettings" && active == true][0]'
            )
            
            config_data = result.get('result')
            if not config_data:
                logger.warning("No active platform settings found")
                return None
            
            return PlatformConfig(
                facebook=config_data.get('facebook', {}),
                instagram=config_data.get('instagram', {}),
                blog=config_data.get('blog', {}),
                cross_platform_settings=config_data.get('crossPlatformSettings', {})
            )
            
        except Exception as e:
            logger.error(f"Error loading platform config: {e}")
            return None
    
    @property
    def content_strategy(self) -> ContentStrategyConfig:
        """Get content strategy configuration"""
        if not self._content_strategy:
            raise ValueError("Content strategy not loaded. Call load_all_configurations() first.")
        return self._content_strategy
    
    @property
    def seasonal_config(self) -> SeasonalConfig:
        """Get seasonal configuration"""
        if not self._seasonal_config:
            raise ValueError("Seasonal config not loaded. Call load_all_configurations() first.")
        return self._seasonal_config
    
    @property
    def image_config(self) -> ImageGenerationConfig:
        """Get image generation configuration"""
        if not self._image_config:
            raise ValueError("Image config not loaded. Call load_all_configurations() first.")
        return self._image_config
    
    @property
    def platform_config(self) -> PlatformConfig:
        """Get platform configuration"""
        if not self._platform_config:
            raise ValueError("Platform config not loaded. Call load_all_configurations() first.")
        return self._platform_config
    
    def get_pillar_weight(self, pillar: str) -> float:
        """Get weight for specific content pillar"""
        return self.content_strategy.pillar_weights.get(pillar, 0.0)
    
    def get_seasonal_boost(self, pillar: str, content_keywords: list) -> float:
        """Calculate seasonal boost for content based on keywords"""
        current_season = self.seasonal_config.current_season
        seasonal_keywords = self.seasonal_config.seasonal_keywords.get(current_season, [])
        
        # Check if content matches current season
        keyword_matches = sum(1 for keyword in content_keywords if keyword.lower() in [sk.lower() for sk in seasonal_keywords])
        
        if keyword_matches > 0:
            return self.seasonal_config.seasonal_boosts.get('currentSeasonBoost', 1.0)
        else:
            return self.seasonal_config.seasonal_boosts.get('offSeasonPenalty', 0.3)
    
    def get_platform_for_content(self, content_length: int, content_type: str) -> str:
        """Determine optimal platform for content based on characteristics"""
        # Platform selection logic based on content characteristics
        if content_type == 'video' or 'video' in content_type.lower():
            return 'Instagram'
        elif content_length > self.platform_config.facebook['contentLength']['max']:
            return 'Blog'
        elif content_length < self.platform_config.instagram['contentLength']['optimal']:
            return 'Instagram'
        else:
            return 'Facebook'
    
    def get_enhancement_prompt(self, pillar: str) -> str:
        """Get image enhancement prompt for specific content pillar"""
        return self.image_config.enhancement_prompts.get(pillar, 
            "Enhance this equipment image with professional lighting and clean background.")
    
    def refresh_configurations(self) -> bool:
        """Refresh all configurations from Sanity"""
        self._content_strategy = None
        self._seasonal_config = None
        self._image_config = None
        self._platform_config = None
        return self.load_all_configurations()