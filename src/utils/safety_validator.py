# utils/safety_validator.py
"""Safety validation system for social media content to prevent dangerous recommendations."""

import re
import os
import logging
from typing import Dict, List, Tuple
from src.utils.gemini_helpers import call_gemini_api
from sanity import Client

# Initialize Sanity client for fetching safety prompts
SANITY_PROJECT_ID = os.environ.get("SANITY_PROJECT_ID", "2pxuaj9k")
SANITY_DATASET = os.environ.get("SANITY_DATASET", "production")
SANITY_API_TOKEN = os.environ.get("SANITY_API_TOKEN")

logger = logging.getLogger(__name__)

sanity_client = Client(
    project_id=SANITY_PROJECT_ID,
    dataset=SANITY_DATASET,
    token=SANITY_API_TOKEN,
    use_cdn=True,
    logger=logger
)

class SafetyValidator:
    """Validates social media content for safety issues and dangerous recommendations."""
    
    def __init__(self):
        self.dangerous_keywords = {
            'ice': ['ice fishing', 'frozen lake', 'winter ice', 'ice surface'],
            'height': ['roof', 'ladder', 'climbing', 'elevated'],
            'water': ['underwater', 'submerged', 'flooding', 'deep water'],
            'electrical': ['live wire', 'electrical', 'power line'],
            'weather': ['storm', 'severe weather', 'high wind', 'lightning']
        }
        
        self.equipment_weight_limits = {
            'mini-excavator': {'weight_tons': 2, 'ice_safe': False},
            'skid steer': {'weight_tons': 3, 'ice_safe': False}, 
            'excavator': {'weight_tons': 20, 'ice_safe': False},
            'bulldozer': {'weight_tons': 15, 'ice_safe': False},
            'compactor': {'weight_tons': 5, 'ice_safe': False}
        }

    def validate_content_safety(self, idea: Dict) -> Tuple[bool, List[str]]:
        """
        Validate if content contains dangerous recommendations.
        Returns (is_safe, list_of_issues)
        """
        issues = []
        title = idea.get('title', '').lower()
        body = idea.get('body', '').lower()
        content = f"{title} {body}"
        
        # Check for ice + heavy equipment combinations
        if self._contains_ice_context(content) and self._contains_heavy_equipment(content):
            issues.append("DANGER: Recommends using heavy equipment on ice - extreme fall-through risk")
        
        # Check for height-related safety issues
        if self._contains_height_risks(content):
            issues.append("WARNING: Contains height-related activities without safety mentions")
        
        # Check for weather-related risks
        if self._contains_weather_risks(content):
            issues.append("WARNING: Recommends equipment use in dangerous weather conditions")
        
        # Use AI for contextual safety validation
        ai_safety_check = self._ai_safety_validation(content)
        if ai_safety_check:
            issues.extend(ai_safety_check)
        
        is_safe = len(issues) == 0
        return is_safe, issues

    def _contains_ice_context(self, content: str) -> bool:
        """Check if content mentions ice/frozen surfaces."""
        ice_terms = ['ice', 'frozen', 'winter lake', 'ice fishing', 'frozen pond']
        return any(term in content for term in ice_terms)
    
    def _contains_heavy_equipment(self, content: str) -> bool:
        """Check if content mentions heavy equipment."""
        return any(equipment in content for equipment in self.equipment_weight_limits.keys())
    
    def _contains_height_risks(self, content: str) -> bool:
        """Check for height-related risks."""
        height_terms = ['roof', 'ladder', 'elevated', 'climbing', 'overhead']
        return any(term in content for term in height_terms)
    
    def _contains_weather_risks(self, content: str) -> bool:
        """Check for dangerous weather conditions."""
        weather_terms = ['storm', 'high wind', 'lightning', 'severe weather']
        return any(term in content for term in weather_terms)
    
    def _get_safety_prompt_from_sanity(self) -> str:
        """Extract safety guidelines from the main content generation prompt."""
        try:
            query_result = sanity_client.query(
                '*[_type == "contentPrompt" && title == "Content Generation Prompt"][0]'
            )
            content_prompt_doc = query_result.get('result')
            if content_prompt_doc:
                main_prompt = content_prompt_doc.get('content', '')
                # Create safety-focused validation prompt based on main guidelines
                return f"""
                Based on these content guidelines: {main_prompt}
                
                Analyze this social media content for safety violations:
                "{{content}}"
                
                Check for dangerous recommendations including:
                1. Heavy equipment on ice/frozen surfaces (NEVER SAFE)
                2. Equipment misuse or unsafe applications
                3. Violations of the safety standards mentioned in guidelines
                
                Respond with ONLY a JSON array of safety concerns, or [] if safe:
                """
            return self._get_fallback_safety_prompt()
        except Exception as e:
            print(f"Error fetching content prompt from Sanity: {e}")
            return self._get_fallback_safety_prompt()
    
    def _get_fallback_safety_prompt(self) -> str:
        """Fallback safety prompt if Sanity is unavailable."""
        return """
        Analyze this social media content for potential safety issues or dangerous recommendations:
        
        "{content}"
        
        Check for:
        1. Heavy equipment on ice/frozen surfaces (extremely dangerous - equipment can fall through)
        2. Equipment use without proper safety measures
        3. Dangerous work environments
        4. Improper equipment applications
        5. Weather-related safety concerns
        
        Respond with ONLY a JSON array of specific safety concerns, or empty array [] if safe:
        ["concern 1", "concern 2"]
        
        Be very strict about ice safety - NO heavy equipment should EVER be on ice.
        """

    def _ai_safety_validation(self, content: str) -> List[str]:
        """Use AI to validate content for safety issues."""
        try:
            safety_prompt_template = self._get_safety_prompt_from_sanity()
            safety_prompt = safety_prompt_template.replace("{content}", content)
            
            response = call_gemini_api(safety_prompt)
            if response:
                # Try to parse JSON response
                import json
                try:
                    concerns = json.loads(response.strip())
                    return concerns if isinstance(concerns, list) else []
                except:
                    # If JSON parsing fails, check for key safety phrases in response
                    if 'ice' in response.lower() and ('danger' in response.lower() or 'unsafe' in response.lower()):
                        return ["AI detected ice safety concerns"]
            return []
        except Exception as e:
            print(f"Error in AI safety validation: {e}")
            return []

    def _get_safe_alternative_prompt_from_sanity(self) -> str:
        """Fetch safe alternative generation prompt from Sanity CMS."""
        try:
            query_result = sanity_client.query(
                '*[_type == "contentPrompt" && promptType == "safeAlternativeGeneration"][0]'
            )
            prompt_doc = query_result.get('result')
            if prompt_doc:
                return prompt_doc.get('content', self._get_fallback_alternative_prompt())
            return self._get_fallback_alternative_prompt()
        except Exception as e:
            print(f"Error fetching safe alternative prompt from Sanity: {e}")
            return self._get_fallback_alternative_prompt()
    
    def _get_fallback_alternative_prompt(self) -> str:
        """Fallback alternative generation prompt."""
        return """
        The following social media content was flagged as unsafe:
        Title: {title}
        Body: {body}
        
        Create a SAFE alternative that:
        1. Promotes the same equipment rental
        2. Shows appropriate, safe use cases
        3. Emphasizes safety and proper applications
        4. Avoids dangerous scenarios (no heavy equipment on ice!)
        
        Return only the new, safe body text:
        """

    def suggest_safe_alternative(self, original_idea: Dict) -> str:
        """Suggest a safer alternative for flagged content."""
        try:
            alternative_prompt_template = self._get_safe_alternative_prompt_from_sanity()
            alternative_prompt = alternative_prompt_template.replace("{title}", original_idea.get('title', '')).replace("{body}", original_idea.get('body', ''))
            
            response = call_gemini_api(alternative_prompt)
            return response.strip() if response else "Safe alternative could not be generated"
        except Exception as e:
            return f"Error generating safe alternative: {e}"

def validate_idea_safety(idea: Dict) -> Tuple[bool, List[str], str]:
    """
    Main function to validate idea safety.
    Returns (is_safe, issues_list, safe_alternative_if_needed)
    """
    validator = SafetyValidator()
    is_safe, issues = validator.validate_content_safety(idea)
    
    safe_alternative = ""
    if not is_safe:
        safe_alternative = validator.suggest_safe_alternative(idea)
    
    return is_safe, issues, safe_alternative