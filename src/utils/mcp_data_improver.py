import json
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional
# Use absolute import for package/module best practice
from src.utils.openai_helpers import call_openai_api, OpenAIRateLimitError

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

@dataclass
class EnhancementConfig:
    """Configuration for AI enhancement process"""
    enhance_descriptions: bool = True
    enhance_specifications: bool = False  # Risky - keep manual
    enhance_use_cases: bool = True
    enhance_keywords: bool = True
    enhance_safety: bool = False  # Risky - keep manual
    enhance_pricing: bool = False  # Risky - keep manual
    confidence_threshold: float = 0.8
    max_tokens: int = 500
    force_enhance: bool = True  # NEW: Always enhance, even if field is populated
    debug: bool = True  # NEW: Print debug info

@dataclass
class EnhancementResult:
    """Result of AI enhancement"""
    field_name: str
    original_value: str
    enhanced_value: str
    confidence_score: float
    source: str = "ai_generated"
    reviewed: bool = False

class AIProductEnhancer:
    """AI-powered product data enhancement with safety guardrails"""
    
    def __init__(self, config: EnhancementConfig):
        self.config = config
        self.enhancement_log = []
        
        # Define safe enhancement categories
        self.safe_enhancements = {
            'marketing_description': True,
            'use_cases': True,
            'keywords': True,
            'project_types': True,
            'industry_applications': True
        }
        
        # Define risky categories that need human review
        self.risky_enhancements = {
            'technical_specifications': False,
            'safety_requirements': False,
            'pricing': False,
            'compliance': False,
            'weight_capacity': False
        }
    
    def create_enhancement_prompt(self, product: Dict, enhancement_type: str) -> str:
        """Create AI prompt for specific enhancement type"""
        
        base_context = f"""
        Product: {product.get('name', 'Unknown')}
        Category: {', '.join(product.get('categories', []))}
        Current Description: {product.get('short_description', '')[:200]}...
        
        Equipment Rental Context: This is for a Canadian equipment rental company.
        """
        
        prompts = {
            'marketing_description': f"""
            {base_context}
            
            Create a compelling, professional marketing description for this rental equipment.
            Focus on:
            - Benefits to the customer
            - Time and labor savings
            - Professional results
            - Cost-effectiveness of renting vs buying
            
            Keep it under 150 words. Be enthusiastic but factual.
            DO NOT include specific technical specifications, weights, or capacities.
            """,
            
            'use_cases': f"""
            {base_context}
            
            List 5-8 specific use cases for this equipment. Format as a JSON array.
            Focus on practical applications customers would recognize.
            Be specific about project types, not just general categories.
            
            Example format: ["Landscaping large residential properties", "Clearing overgrown trails"]
            """,
            
            'keywords': f"""
            {base_context}
            
            Generate 15-20 relevant search keywords for this equipment.
            Include:
            - Equipment type variations
            - Application keywords
            - Industry terms
            - Common search phrases
            
            Format as JSON array. Focus on terms customers actually search for.
            """,
            
            'project_types': f"""
            {base_context}
            
            List specific project types this equipment would be used for.
            Format as JSON array of 5-8 items.
            Be specific about the actual projects, not general categories.
            
            Example: ["Driveway grading", "Basement excavation", "Fence post installation"]
            """
        }
        
        return prompts.get(enhancement_type, prompts['marketing_description'])
    
    def enhance_product_safely(self, product: Dict) -> Tuple[Dict, List[EnhancementResult]]:
        """Enhance product data with safety checks"""
        enhanced_product = product.copy()
        enhancements = []
        
        # Only enhance safe categories
        safe_enhancements = [
            ('marketing_description', 'short_description'),
            ('use_cases', 'primary_use_cases'),
            ('keywords', 'keywords'),
            ('project_types', 'project_types')
        ]
        
        for enhancement_type, field_name in safe_enhancements:
            should_enhance = self._should_enhance_field(product, field_name)
            if self.config.debug:
                logger.info(f"[DEBUG] Product: {product.get('name', 'unknown')} | Field: {field_name} | Should enhance: {should_enhance}")
            if not should_enhance and not self.config.force_enhance:
                if self.config.debug:
                    logger.info(f"[DEBUG] Skipping enhancement for {field_name} (already populated)")
                continue
            try:
                result = self._call_ai_enhancement(product, enhancement_type)
                print(f"[DEBUG] AI result for {product.get('name', 'unknown')} field {field_name}: {result}")
                if not result:
                    # Fallback for debugging: use a dummy value
                    result = f"DUMMY_{enhancement_type}_for_{product.get('name', 'unknown')}"
                    print(f"[DEBUG] Using fallback dummy value for {field_name}: {result}")
                if result and self._validate_enhancement(result, enhancement_type):
                    # Store enhancement result
                    enhancement = EnhancementResult(
                        field_name=field_name,
                        original_value=str(product.get(field_name, '')),
                        enhanced_value=result,
                        confidence_score=0.85,  # Would come from AI model
                        source="ai_generated"
                    )
                    enhancements.append(enhancement)
                    # Apply safe enhancements
                    if enhancement_type == 'marketing_description':
                        enhanced_product['ai_enhanced_description'] = result
                    elif enhancement_type == 'use_cases':
                        enhanced_product['ai_suggested_use_cases'] = result
                    elif enhancement_type == 'keywords':
                        enhanced_product['ai_keywords'] = result
                    elif enhancement_type == 'project_types':
                        enhanced_product['ai_project_types'] = result
                else:
                    if self.config.debug:
                        logger.info(f"[DEBUG] Validation failed or empty result for {field_name}")
            except OpenAIRateLimitError:
                # Suppress all output for rate limits, propagate up
                raise
            except Exception as e:
                logger.error(f"AI enhancement failed for {product.get('name', 'unknown')}: {e}")
                continue
        return enhanced_product, enhancements
    
    def _should_enhance_field(self, product: Dict, field_name: str) -> bool:
        """Determine if field should be enhanced"""
        current_value = product.get(field_name, '')
        # Don't enhance if field is already well-populated
        if isinstance(current_value, str) and len(current_value) > 100:
            return False
        elif isinstance(current_value, list) and len(current_value) > 3:
            return False
        return True
    
    def _call_ai_enhancement(self, product: Dict, enhancement_type: str) -> Optional[str]:
        """Call AI service for enhancement using the OpenAI API helper."""
        prompt = self.create_enhancement_prompt(product, enhancement_type)
        try:
            response_text = call_openai_api(prompt)
            if response_text:
                cleaned_response = response_text.strip().replace("```json", "").replace("```", "").strip()
                # Attempt to parse JSON for use_cases, keywords, project_types
                if enhancement_type in ['use_cases', 'keywords', 'project_types']:
                    try:
                        return json.loads(cleaned_response)
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse JSON for {enhancement_type}. Returning raw text.")
                        return cleaned_response
                return cleaned_response
            return None
        except Exception as e:
            logger.error(f"AI enhancement failed for {product.get('name', 'unknown')} with {enhancement_type}: {e}")
            return None
    
    def _validate_enhancement(self, result: str, enhancement_type: str) -> bool:
        """Validate AI enhancement result"""
        if not result:
            return False
        # Basic validation rules
        validations = {
            'marketing_description': lambda r: len(r) < 500 and not any(word in r.lower() for word in ['guaranteed', 'best', 'cheapest']),
            'use_cases': lambda r: isinstance(r, (list, str)) and len(str(r)) > 10,
            'keywords': lambda r: isinstance(r, (list, str)) and len(str(r)) > 10,
            'project_types': lambda r: isinstance(r, (list, str)) and len(str(r)) > 10
        }
        validator = validations.get(enhancement_type, lambda r: True)
        return validator(result)
    
    def generate_enhancement_report(self, products: List[Dict]) -> Dict:
        """Generate report on enhancement process"""
        total_products = len(products)
        enhanced_products = 0
        total_enhancements = 0
        enhancement_stats = {
            'marketing_description': 0,
            'use_cases': 0,
            'keywords': 0,
            'project_types': 0
        }
        for product in products:
            if any(key.startswith('ai_') for key in product.keys()):
                enhanced_products += 1
            for key in product.keys():
                if key.startswith('ai_'):
                    total_enhancements += 1
                    base_key = key.replace('ai_', '').replace('_suggested', '').replace('_enhanced', '')
                    if base_key in enhancement_stats:
                        enhancement_stats[base_key] += 1
        return {
            'total_products': total_products,
            'enhanced_products': enhanced_products,
            'enhancement_rate': enhanced_products / total_products if total_products > 0 else 0,
            'total_enhancements': total_enhancements,
            'enhancement_breakdown': enhancement_stats,
            'generated_at': datetime.now().isoformat()
        }

def enhance_rental_catalog(catalog_path: str, output_path: str, config: EnhancementConfig = None, wait_seconds: float = 2.0):
    import time
    import sys
    if config is None:
        config = EnhancementConfig()
    # Load existing catalog
    with open(catalog_path, 'r') as f:
        catalog_data = json.load(f)
    enhancer = AIProductEnhancer(config)
    products = catalog_data.get('product_catalog', [])
    total_products = len(products)
    logger.info(f"Starting AI enhancement of {total_products} products...")
    all_enhancements = []
    processed_products = []
    error_count = 0
    try:
        for idx, product in enumerate(products):
            try:
                if config.debug:
                    logger.info(f"[DEBUG] Enhancing product {idx+1}/{total_products}: {product.get('name', 'Unknown')}")
                enhanced_product, enhancements = enhancer.enhance_product_safely(product)
                processed_products.append(enhanced_product)
                all_enhancements.extend(enhancements)
            except OpenAIRateLimitError as e:
                logger.error(f"OpenAI rate limit hit. Stopping enhancement. Error: {e}")
                raise  # Re-raise to stop the script
            except Exception as e:
                error_count += 1
                logger.error(f"Skipped product {idx+1} ({product.get('name', 'Unknown')}): {e}")
                processed_products.append(product)  # Add original product back if enhancement fails
            # Print progress bar
            bar_len = 30
            filled_len = int(bar_len * (idx + 1) / total_products)
            bar = '=' * filled_len + '-' * (bar_len - filled_len)
            sys.stdout.write(f"\r[Progress] |{bar}| {idx+1}/{total_products} products processed.")
            sys.stdout.flush()
            time.sleep(wait_seconds)
    except (KeyboardInterrupt, OpenAIRateLimitError):
        print("\nEnhancement process stopped. No file will be saved.")
        return
    # Prepare the complete catalog data
    complete_catalog = catalog_data.copy()
    complete_catalog['product_catalog'] = processed_products
    complete_catalog['ai_enhancement'] = {
        'enabled': True,
        'config': asdict(config),
        'enhancement_report': enhancer.generate_enhancement_report(processed_products),
        'enhancement_log': [asdict(e) for e in all_enhancements if hasattr(e, '__dataclass_fields__')],
        'processing_metadata': {
            'last_save_timestamp': datetime.now().isoformat(),
            'total_products': total_products,
            'products_processed': len(processed_products),
            'total_errors': error_count
        },
        'safety_note': 'AI enhancements are suggestions only. Technical specifications and safety information remain unchanged.'
    }
    # Write the enhanced data to the output file
    with open(output_path, 'w') as f:
        json.dump(complete_catalog, f, indent=2)
    print(f"\n✅ Enhancement complete! Processed: {len(processed_products)} products. Errors: {error_count}.")
    logger.info(f"📊 Enhanced {len(processed_products)} products")
    logger.info(f"🔧 Total enhancements: {len(all_enhancements)}")
    logger.info(f"⚠️  Safety note: Technical specs and safety info unchanged")

if __name__ == "__main__":
    # Example usage: enhance the catalog and write to a new file.
    enhance_rental_catalog(
        catalog_path="src/data/mcp_rental_catalog.json",
        output_path="src/data/mcp_rental_catalog_enhanced.json",
        wait_seconds=2.0
    )
    print("Enhancement complete. See src/data/mcp_rental_catalog_enhanced.json for results.")