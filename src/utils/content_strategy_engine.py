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
        
        # Content pillar mapping using actual Sanity categories
        self.pillar_categories = {
            'equipment_spotlight': ['Earth Moving Equipment', 'Concrete Equipment', 'Lift-Scaffold-Fence', 'Compaction Equipment'],
            'project_showcase': ['Earth Moving Equipment', 'Concrete Equipment', 'Drills & Breakers', 'Saws'],
            'industry_focus': ['Earth Moving Equipment', 'Lawn & Garden', 'Concrete Equipment', 'Moving Equipment'],
            'seasonal_content': ['Lawn Care', 'Heating', 'Generators & Cords', 'Pumps: Gas & Electric'],
            'safety_training': ['Drills & Breakers', 'Lift-Scaffold-Fence', 'Saws', 'Earth Moving Equipment'],
            'educational_content': ['Hand Tools', 'Measuring Equipment', 'Floor Equipment', 'Fastening Tools'],
            'customer_success': ['Earth Moving Equipment', 'Concrete Equipment', 'Lifts'],
            'maintenance_tips': ['Generators & Cords', 'Pumps: Gas & Electric', 'Air Compressors & Tools']
        }
    
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
        """Select content pillar based on weighted strategy"""
        weights = self.config.content_strategy.pillar_weights
        
        # Create weighted selection
        pillars = list(weights.keys())
        probabilities = list(weights.values())
        
        # Normalize probabilities
        total = sum(probabilities)
        if total > 0:
            probabilities = [p / total for p in probabilities]
        else:
            # Fallback to equal weights
            probabilities = [1.0 / len(pillars)] * len(pillars)
        
        # Apply seasonal boost
        current_season = self.config.seasonal_config.current_season
        seasonal_boost = self.config.seasonal_config.seasonal_boosts.get('currentSeasonBoost', 1.0)
        
        # Boost seasonal content during current season
        for i, pillar in enumerate(pillars):
            if pillar == 'seasonal_content':
                probabilities[i] *= seasonal_boost
        
        # Renormalize
        total = sum(probabilities)
        probabilities = [p / total for p in probabilities]
        
        # Weighted random selection
        selected_pillar = random.choices(pillars, weights=probabilities)[0]
        
        logger.debug(f"Selected pillar: {selected_pillar} (weight: {weights.get(selected_pillar, 0)})")
        return selected_pillar
    
    def _select_optimal_platform(self, pillar: str) -> str:
        """Select optimal platform based on pillar characteristics"""
        platform_preferences = self.config.content_strategy.platform_preferences
        
        # Pillar-specific platform optimization
        if pillar == 'equipment_spotlight':
            # Equipment spotlight works well on Instagram (visual) and Facebook (detailed)
            return random.choices(['Instagram', 'Facebook'], weights=[0.6, 0.4])[0]
        elif pillar == 'project_showcase':
            # Project showcases are visual and work great on Instagram
            return random.choices(['Instagram', 'Facebook'], weights=[0.7, 0.3])[0]
        elif pillar == 'educational_content':
            # Educational content works best on Blog and Facebook
            return random.choices(['Blog', 'Facebook'], weights=[0.6, 0.4])[0]
        elif pillar == 'safety_training':
            # Safety content should be comprehensive - Blog preferred
            return random.choices(['Blog', 'Facebook'], weights=[0.8, 0.2])[0]
        else:
            # Use configured platform preferences
            platforms = list(platform_preferences.keys())
            weights = list(platform_preferences.values())
            
            # Normalize weights
            total = sum(weights)
            if total > 0:
                weights = [w / total for w in weights]
                return random.choices(platforms, weights=weights)[0]
            else:
                return 'Facebook'  # Default fallback
    
    def _select_equipment_category(self, pillar: str) -> str:
        """Select equipment category based on pillar and business strategy"""
        # Get pillar-appropriate categories
        available_categories = self.pillar_categories.get(pillar, ['Earth Moving Equipment'])
        
        if pillar == 'seasonal_content':
            # Use seasonal equipment priorities
            current_season = self.config.seasonal_config.current_season
            seasonal_priorities = self.config.seasonal_config.seasonal_equipment_priority.get(current_season, [])
            
            if seasonal_priorities:
                # Convert seasonal priorities to actual Sanity categories
                category_mapping = {
                    'landscaping': 'Lawn & Garden',
                    'construction': 'Earth Moving Equipment', 
                    'snow-removal': 'Moving Equipment',
                    'agriculture': 'Tillers',
                    'material-handling': 'Moving Equipment',
                    'leaf-blowers': 'Blower/Sprayer',
                    'chippers': 'Wood Chipper',
                    'excavation': 'Earth Moving Equipment',
                    'cleanup': 'Moving Equipment',
                    'heaters': 'Heating',
                    'indoor-tools': 'Hand Tools',
                    'pumps': 'Pumps: Gas & Electric',
                    'generators': 'Generators & Cords'
                }
                
                seasonal_categories = [category_mapping.get(p, 'Lawn & Garden') for p in seasonal_priorities]
                available_seasonal = [cat for cat in seasonal_categories if cat in self.pillar_categories.get(pillar, [])]
                if available_seasonal:
                    return random.choice(available_seasonal)
                else:
                    return random.choice(seasonal_categories)
        
        # Apply business rules
        equipment_rules = self.config.content_strategy.equipment_selection_rules
        
        if equipment_rules.get('prioritizeHighMargin', False):
            # Prioritize high-margin categories (would need margin data)
            high_margin_categories = ['Compaction', 'Concrete', 'Demolition']
            available_high_margin = [cat for cat in high_margin_categories if cat in available_categories]
            if available_high_margin:
                return random.choice(available_high_margin)
        
        # Default to random selection from available categories
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
        """Calculate priority score for content plan"""
        base_score = 50.0
        
        # Pillar weight contribution (0-40 points)
        pillar_weight = self.config.content_strategy.pillar_weights.get(pillar, 0.1)
        score = base_score + (pillar_weight * 40)
        
        # Seasonal boost (multiply by 1.0-2.0)
        current_season = self.config.seasonal_config.current_season
        if 'seasonal' in pillar.lower() or current_season.lower() in seasonal_context.lower():
            seasonal_boost = self.config.seasonal_config.seasonal_boosts.get('currentSeasonBoost', 1.0)
            score *= seasonal_boost
        
        # Equipment availability bonus (+10 points if available equipment)
        try:
            equipment_count = self._get_available_equipment_count(equipment_category)
            if equipment_count > 0:
                score += min(equipment_count * 2, 10)  # Max 10 bonus points
        except Exception as e:
            logger.warning(f"Could not check equipment availability: {e}")
        
        # Business rules bonus
        equipment_rules = self.config.content_strategy.equipment_selection_rules
        if equipment_rules.get('prioritizeNewEquipment', False):
            score += 5  # Bonus for featuring new equipment
        
        return min(score, 100.0)  # Cap at 100
    
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