#!/usr/bin/env python3
"""
Content Strategy Engine for Enhanced Content Generation
Implements strategic content planning based on business objectives and data-driven decisions.
"""

import random
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from sanity import Client

from .config_loader import ConfigurationLoader

logger = logging.getLogger(__name__)

@dataclass
class ContentPlan:
    """Strategic content plan for generation"""
    pillar: str
    target_platform: str
    equipment_category: str
    seasonal_context: str
    priority_score: float
    business_rationale: str

@dataclass
class EquipmentTarget:
    """Equipment targeting information"""
    category: str
    specific_equipment_ids: List[str]
    availability_filter: str
    priority_reasons: List[str]

class ContentStrategyEngine:
    """Strategic content planning engine"""
    
    def __init__(self, config_loader: ConfigurationLoader, sanity_client: Client):
        self.config = config_loader
        self.sanity_client = sanity_client
        
        # Cache for available categories to avoid repeated queries
        self._categories_cache = None
        
        # Simple content pillars without hardcoded category mappings
        self.content_pillars = [
            'equipment_spotlight',
            'project_showcase', 
            'seasonal_content',
            'safety_training',
            'educational_content',
            'industry_focus',
            'customer_success',
            'maintenance_tips'
        ]
    
    def plan_strategic_content(self, num_ideas: int = 1) -> List[ContentPlan]:
        """Create strategic content plans based on business objectives"""
        logger.info(f"Planning {num_ideas} strategic content ideas...")
        
        plans = []
        
        for i in range(num_ideas):
            # 1. Strategic pillar selection
            pillar = self._select_strategic_pillar()
            
            # 2. Platform selection based on pillar
            platform = self._select_optimal_platform(pillar)
            
            # 3. Equipment category targeting
            equipment_category = self._select_equipment_category(pillar)
            
            # 4. Seasonal context
            seasonal_context = self._get_seasonal_context(pillar)
            
            # 5. Calculate priority score
            priority_score = self._calculate_priority_score(pillar, equipment_category, seasonal_context)
            
            # 6. Business rationale
            rationale = self._generate_business_rationale(pillar, equipment_category, seasonal_context)
            
            plan = ContentPlan(
                pillar=pillar,
                target_platform=platform,
                equipment_category=equipment_category,
                seasonal_context=seasonal_context,
                priority_score=priority_score,
                business_rationale=rationale
            )
            
            plans.append(plan)
            logger.info(f"Plan {i+1}: {pillar} for {platform} - Score: {priority_score:.2f}")
        
        # Sort by priority score (highest first)
        plans.sort(key=lambda p: p.priority_score, reverse=True)
        
        return plans
    
    def _select_strategic_pillar(self) -> str:
        """Select content pillar randomly"""
        # Pure random selection from available pillars
        selected_pillar = random.choice(self.content_pillars)
        logger.debug(f"Selected pillar: {selected_pillar}")
        return selected_pillar
    
    def _select_optimal_platform(self, pillar: str) -> str:
        """Select platform randomly"""
        # Simple random platform selection
        platforms = ['Facebook', 'Instagram', 'Blog']
        return random.choice(platforms)
    
    def _select_equipment_category(self, pillar: str) -> str:
        """Select equipment category randomly from all available categories"""
        # Get all available categories from Sanity
        available_categories = self._get_available_categories()
        
        if not available_categories:
            logger.warning("No equipment categories available, using fallback")
            return 'Hand Tools'
        
        # Simple random selection from all available categories
        # No hardcoded mappings or complex business rules - just pure randomization
        return random.choice(available_categories)
    
    def _get_seasonal_context(self, pillar: str) -> str:
        """Get seasonal context for content"""
        current_season = self.config.seasonal_config.current_season
        seasonal_themes = self.config.seasonal_config.seasonal_content_themes.get(current_season, [])
        
        if pillar == 'seasonal_content' and seasonal_themes:
            return random.choice(seasonal_themes)
        else:
            return f"{current_season.title()} Context"
    
    def _calculate_priority_score(self, pillar: str, equipment_category: str, seasonal_context: str) -> float:
        """Simple priority score - just randomize"""
        # Simple random score between 50-100
        return random.uniform(50.0, 100.0)
    
    def _get_available_categories(self) -> List[str]:
        """Get all available equipment categories from Sanity"""
        if self._categories_cache is not None:
            return self._categories_cache
        
        try:
            result = self.sanity_client.query('*[_type == "equipment"]{ categories }')
            categories = set()
            
            for item in result.get('result', []):
                if item.get('categories'):
                    categories.update(item['categories'])
            
            self._categories_cache = list(categories)
            logger.info(f"Cached {len(self._categories_cache)} equipment categories")
            return self._categories_cache
            
        except Exception as e:
            logger.error(f"Error fetching categories: {e}")
            return ['Hand Tools', 'Lawn & Garden', 'Concrete Equipment']  # Fallback
    
    def _get_available_equipment_count(self, category: str) -> int:
        """Get count of available equipment in category"""
        try:
            result = self.sanity_client.query(
                f'count(*[_type == "equipment" && availability.status == "available" && "{category}" in categories[]])'
            )
            return result.get('result', 0)
        except Exception as e:
            logger.error(f"Error counting equipment in category {category}: {e}")
            return 0
    
    def _generate_business_rationale(self, pillar: str, equipment_category: str, seasonal_context: str) -> str:
        """Generate business rationale for content plan"""
        rationales = []
        
        # Pillar rationale
        pillar_rationales = {
            'equipment_spotlight': "Showcase specific equipment to drive rental interest",
            'project_showcase': "Demonstrate equipment in action to build customer confidence",
            'seasonal_content': "Capitalize on seasonal rental demand",
            'safety_training': "Build trust through safety education and compliance",
            'educational_content': "Establish expertise and support customer decision-making",
            'industry_focus': "Target specific industry segments for growth",
            'customer_success': "Leverage social proof to attract new customers",
            'maintenance_tips': "Add value and extend customer relationships"
        }
        
        rationales.append(pillar_rationales.get(pillar, "Strategic content generation"))
        
        # Equipment category rationale
        if equipment_category:
            rationales.append(f"Focus on {equipment_category} equipment for targeted impact")
        
        # Seasonal rationale
        current_season = self.config.seasonal_config.current_season
        if current_season.lower() in seasonal_context.lower():
            rationales.append(f"Leverage {current_season} demand patterns")
        
        return "; ".join(rationales)
    
    def get_equipment_targets(self, plan: ContentPlan) -> EquipmentTarget:
        """Get specific equipment targeting based on content plan"""
        try:
            # Build equipment query based on plan
            category_filter = f'"{plan.equipment_category}" in categories[]'
            availability_filter = 'availability.status == "available"'
            
            # Apply business rules
            equipment_rules = self.config.content_strategy.equipment_selection_rules
            
            filters = [f'_type == "equipment"', availability_filter, category_filter]
            
            # Add additional filters based on rules
            if equipment_rules.get('excludeUnavailable', True):
                pass  # Already included in availability_filter
            
            # Optional: prioritize new equipment (but don't require it)
            # This will be handled in the sorting logic instead of filtering
            
            # Combine filters
            full_filter = ' && '.join(filters)
            
            # Execute query
            query = f'*[{full_filter}]{{_id, name, brand, availability, popularity_score, _createdAt}}'
            result = self.sanity_client.query(query)
            equipment_list = result.get('result', [])
            
            # Apply prioritization
            if equipment_rules.get('prioritizeUnderutilized', False):
                # Sort by popularity_score (ascending - less popular first)
                equipment_list.sort(key=lambda x: x.get('popularity_score') or 0)
            else:
                # Sort by popularity_score (descending - most popular first)
                equipment_list.sort(key=lambda x: x.get('popularity_score') or 0, reverse=True)
            
            # Limit to top equipment
            max_equipment = equipment_rules.get('maxEquipmentPerPost', 3)
            selected_equipment = equipment_list[:max_equipment]
            
            equipment_ids = [eq['_id'] for eq in selected_equipment]
            
            # Generate priority reasons
            priority_reasons = []
            if equipment_rules.get('prioritizeNewEquipment', False):
                priority_reasons.append("Recently added equipment")
            if equipment_rules.get('prioritizeUnderutilized', False):
                priority_reasons.append("Underutilized equipment needing promotion")
            if plan.seasonal_context:
                priority_reasons.append(f"Seasonal relevance for {plan.seasonal_context}")
            
            return EquipmentTarget(
                category=plan.equipment_category,
                specific_equipment_ids=equipment_ids,
                availability_filter=availability_filter,
                priority_reasons=priority_reasons
            )
            
        except Exception as e:
            logger.error(f"Error getting equipment targets: {e}")
            return EquipmentTarget(
                category=plan.equipment_category,
                specific_equipment_ids=[],
                availability_filter='availability.status == "available"',
                priority_reasons=["Default equipment selection"]
            )
    
    def analyze_content_performance(self) -> Dict[str, Any]:
        """Analyze past content performance to inform strategy"""
        try:
            # Get content from last 30 days with engagement data
            result = self.sanity_client.query(
                '''*[_type == "socialContent" && _createdAt > dateTime(now()) - 30*24*60*60] {
                    contentPillar, platform, _createdAt, published,
                    "equipmentCount": count(related_equipment)
                }'''
            )
            
            content_data = result.get('result', [])
            
            analysis = {
                'total_content': len(content_data),
                'pillar_distribution': {},
                'platform_distribution': {},
                'equipment_usage': {},
                'recommendations': []
            }
            
            # Analyze pillar distribution
            for content in content_data:
                pillar = content.get('contentPillar', 'unknown')
                analysis['pillar_distribution'][pillar] = analysis['pillar_distribution'].get(pillar, 0) + 1
                
                platform = content.get('platform', 'unknown')
                analysis['platform_distribution'][platform] = analysis['platform_distribution'].get(platform, 0) + 1
            
            # Generate recommendations
            if analysis['total_content'] > 0:
                # Check for underrepresented pillars
                pillar_weights = self.config.content_strategy.pillar_weights
                for pillar, target_weight in pillar_weights.items():
                    actual_count = analysis['pillar_distribution'].get(pillar, 0)
                    actual_percentage = actual_count / analysis['total_content']
                    
                    if actual_percentage < target_weight * 0.8:  # 20% tolerance
                        analysis['recommendations'].append(
                            f"Increase {pillar} content (current: {actual_percentage:.1%}, target: {target_weight:.1%})"
                        )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing content performance: {e}")
            return {'error': str(e)}