import os
import json
import re
import html
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from woocommerce import API
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

WOO_COMMERCE_URL = os.getenv("WOO_COMMERCE_URL")
WOO_COMMERCE_CONSUMER_KEY = os.getenv("WOO_COMMERCE_CONSUMER_KEY")
WOO_COMMERCE_CONSUMER_SECRET = os.getenv("WOO_COMMERCE_CONSUMER_SECRET")

@dataclass
class BusinessLocation:
    """Business location information"""
    address: str
    city: str
    province: str
    postal_code: str
    country: str
    phone: str
    email: str
    coordinates: Optional[Dict[str, float]] = None

@dataclass
class BusinessHours:
    """Business operating hours"""
    monday: str
    tuesday: str
    wednesday: str
    thursday: str
    friday: str
    saturday: str
    sunday: str
    seasonal_note: Optional[str] = None

@dataclass
class BusinessInfo:
    """Complete business information"""
    name: str
    slogan: str
    description: str
    website: str
    established: Optional[str]
    location: BusinessLocation
    hours: BusinessHours
    social_media: Dict[str, str]
    certifications: List[str]
    service_areas: List[str]

@dataclass
class ProductImage:
    """Product image information"""
    url: str
    alt_text: str
    is_primary: bool = False
    size: Optional[str] = None

@dataclass
class ProductSpecification:
    """Product technical specifications"""
    name: str
    value: str
    unit: Optional[str] = None
    category: str = "general"

@dataclass
class ProductPricing:
    """Product pricing information"""
    daily_rate: float
    weekly_rate: Optional[float] = None
    monthly_rate: Optional[float] = None
    currency: str = "CAD"
    deposit_required: Optional[float] = None
    minimum_rental_period: str = "1 day"

@dataclass
class ProductAvailability:
    """Product availability information"""
    status: str  # available, unavailable, maintenance, reserved
    quantity_available: int
    next_available_date: Optional[str] = None
    maintenance_schedule: Optional[str] = None

@dataclass
class ProductSafety:
    """Product safety and compliance information"""
    safety_requirements: List[str]
    operator_certification_required: bool
    protective_equipment_required: List[str]
    compliance_standards: List[str]
    age_restrictions: Optional[str] = None

@dataclass
class RentalProduct:
    """Complete rental product information"""
    id: str
    sku: str
    name: str
    slug: str
    categories: List[str]
    subcategories: List[str]
    
    # Descriptions
    short_description: str
    full_description: str
    technical_description: str
    
    # Media
    images: List[ProductImage]
    video_urls: List[str]
    manual_urls: List[str]
    
    # Specifications
    specifications: List[ProductSpecification]
    dimensions: Dict[str, str]
    power_source: str
    
    # Pricing and availability
    pricing: ProductPricing
    availability: ProductAvailability
    
    # Usage information
    primary_use_cases: List[str]
    secondary_use_cases: List[str]
    industries_served: List[str]
    project_types: List[str]
    
    # Safety and compliance
    safety: ProductSafety
    
    # SEO and search
    keywords: List[str]
    search_tags: List[str]
    related_products: List[str]
    
    # Metadata
    created_date: str
    last_updated: str
    review_count: int
    
    # Optional fields with defaults
    brand: Optional[str] = None
    model: Optional[str] = None
    weight: Optional[str] = None
    popularity_score: float = 0.0
    review_rating: Optional[float] = None

@dataclass
class MCPDataStructure:
    """Main MCP data structure"""
    metadata: Dict[str, Any]
    business_info: BusinessInfo
    product_catalog: List[RentalProduct]
    categories: Dict[str, Dict[str, Any]]
    search_index: Dict[str, List[str]]
    operational_data: Dict[str, Any]

class DataProcessor:
    """Enhanced data processing utilities"""
    
    @staticmethod
    def clean_html_content(html_content: str) -> str:
        """Clean HTML content and decode entities"""
        if not html_content:
            return ""
        
        # Remove HTML tags
        clean_text = re.sub(r'<[^>]*>', '', html_content)
        # Decode HTML entities
        clean_text = html.unescape(clean_text)
        # Clean up whitespace
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        # Remove unwanted characters
        clean_text = re.sub(r'[^\w\s\-.,!?()$%/]', '', clean_text)
        
        return clean_text
    
    @staticmethod
    def extract_specifications(description: str) -> List[ProductSpecification]:
        """Extract technical specifications from description"""
        specs = []
        
        # Common specification patterns
        patterns = [
            (r'(\d+)\s*lb[s]?\s*capacity', 'capacity', 'lbs', 'performance'),
            (r'(\d+)\s*hour[s]?\s*(?:battery|working)\s*time', 'battery_life', 'hours', 'power'),
            (r'(\d+)\s*hp\b', 'horsepower', 'hp', 'power'),
            (r'(\d+\.?\d*)\s*inches?\s*cutting\s*(?:height|width)', 'cutting_dimension', 'inches', 'performance'),
            (r'(\d+)\s*(?:mph|km/h)', 'max_speed', 'mph', 'performance'),
            (r'hydraulic\s+dump', 'dump_mechanism', 'hydraulic', 'features'),
        ]
        
        for pattern, name, unit, category in patterns:
            matches = re.findall(pattern, description.lower())
            if matches:
                value = matches[0] if isinstance(matches[0], str) else str(matches[0])
                specs.append(ProductSpecification(
                    name=name,
                    value=value,
                    unit=unit,
                    category=category
                ))
        
        return specs
    
    @staticmethod
    def extract_use_cases(description: str) -> tuple[List[str], List[str]]:
        """Extract primary and secondary use cases"""
        primary_cases = []
        secondary_cases = []
        
        # Primary use case patterns
        primary_patterns = [
            r'(?:ideal|perfect|great|designed)\s+for\s+([^.!?]+)',
            r'use\s+(?:it\s+)?(?:to|for)\s+([^.!?]+)',
            r'suitable\s+for\s+([^.!?]+)'
        ]
        
        # Secondary use case patterns
        secondary_patterns = [
            r'also\s+(?:great|good|suitable)\s+for\s+([^.!?]+)',
            r'can\s+(?:also\s+)?be\s+used\s+for\s+([^.!?]+)'
        ]
        
        for pattern in primary_patterns:
            matches = re.findall(pattern, description.lower())
            primary_cases.extend([match.strip() for match in matches])
        
        for pattern in secondary_patterns:
            matches = re.findall(pattern, description.lower())
            secondary_cases.extend([match.strip() for match in matches])
        
        return primary_cases[:5], secondary_cases[:3]  # Limit results
    
    @staticmethod
    def extract_safety_requirements(description: str) -> ProductSafety:
        """Extract safety requirements from description"""
        safety_reqs = []
        protective_equipment = []
        compliance_standards = []
        
        if 'certification' in description.lower():
            safety_reqs.append('Operator certification recommended')
        
        if 'safety' in description.lower():
            safety_reqs.append('Follow all safety guidelines')
        
        # Check for protective equipment mentions
        protective_terms = ['helmet', 'gloves', 'safety glasses', 'hearing protection']
        for term in protective_terms:
            if term in description.lower():
                protective_equipment.append(term.title())
        
        return ProductSafety(
            safety_requirements=safety_reqs,
            operator_certification_required='certification' in description.lower(),
            protective_equipment_required=protective_equipment,
            compliance_standards=compliance_standards
        )
    
    @staticmethod
    def generate_search_keywords(product: dict, categories: List[str]) -> List[str]:
        """Generate comprehensive search keywords"""
        keywords = set()
        
        # Add name words
        name_words = re.findall(r'\b\w+\b', product['name'].lower())
        keywords.update(name_words)
        
        # Add categories
        keywords.update([cat.lower() for cat in categories])
        
        # Add description keywords
        description = product.get('description', '') + ' ' + product.get('short_description', '')
        desc_words = re.findall(r'\b\w{3,}\b', description.lower())
        keywords.update(desc_words[:20])  # Limit to most relevant
        
        # Add brand/model if available
        if product.get('sku'):
            keywords.add(product['sku'].lower())
        
        return list(keywords)

class WooCommerceDataFetcher:
    """Enhanced WooCommerce data fetcher with MCP formatting"""
    
    def __init__(self):
        self.processor = DataProcessor()
        self.wcapi = self._initialize_api()
        
    def _initialize_api(self) -> API:
        """Initialize WooCommerce API"""
        if not all([WOO_COMMERCE_URL, WOO_COMMERCE_CONSUMER_KEY, WOO_COMMERCE_CONSUMER_SECRET]):
            raise ValueError("WooCommerce API credentials must be set in .env file")
        
        return API(
            url=WOO_COMMERCE_URL,
            consumer_key=WOO_COMMERCE_CONSUMER_KEY,
            consumer_secret=WOO_COMMERCE_CONSUMER_SECRET,
            version="wc/v3"
        )
    
    def _get_business_info(self) -> BusinessInfo:
        """Get comprehensive business information"""
        return BusinessInfo(
            name="Rental Village",
            slogan="Your project. Our equipment. Your satisfaction.",
            description="Professional equipment rental service providing high-quality tools and machinery for construction, landscaping, and home improvement projects.",
            website="https://rentalvillage.ca",
            established="2015",  # Estimated
            location=BusinessLocation(
                address="10348 Cavanagh Road",
                city="Carleton Place",
                province="Ontario",
                postal_code="K7C 4W1",
                country="Canada",
                phone="(613) 257-1669",
                email="info@rentalvillage.ca"
            ),
            hours=BusinessHours(
                monday="7:00 AM - 5:00 PM",
                tuesday="7:00 AM - 5:00 PM",
                wednesday="7:00 AM - 5:00 PM",
                thursday="7:00 AM - 5:00 PM",
                friday="7:00 AM - 5:00 PM",
                saturday="8:00 AM - 4:00 PM",
                sunday="Closed",
                seasonal_note="Summer hours may vary"
            ),
            social_media={
                "facebook": "https://www.facebook.com/RentalVillage/",
                "website": "https://rentalvillage.ca"
            },
            certifications=["Equipment Rental Association Member"],
            service_areas=["Carleton Place", "Ottawa", "Perth", "Lanark County", "Eastern Ontario"]
        )
    
    def _fetch_categories(self) -> Dict[str, Dict[str, Any]]:
        """Fetch and structure product categories"""
        logger.info("Fetching WooCommerce categories...")
        
        try:
            categories_response = self.wcapi.get("products/categories", params={"per_page": 100}).json()
            categories = {}
            
            for cat in categories_response:
                if "id" in cat and "name" in cat:
                    categories[str(cat["id"])] = {
                        "id": cat["id"],
                        "name": html.unescape(cat["name"]),
                        "slug": cat.get("slug", ""),
                        "description": self.processor.clean_html_content(cat.get("description", "")),
                        "parent_id": cat.get("parent", 0),
                        "count": cat.get("count", 0),
                        "image_url": cat.get("image", {}).get("src", "") if cat.get("image") else ""
                    }
            
            return categories
        except Exception as e:
            logger.error(f"Error fetching categories: {e}")
            return {}
    
    def _process_product(self, product: dict, categories_map: Dict[str, Dict[str, Any]]) -> RentalProduct:
        """Process a single product into MCP format"""
        
        # Basic product info
        product_id = str(product["id"])
        name = product["name"]
        slug = product.get("slug", "")
        sku = product.get("sku", "")
        
        # Categories
        product_categories = []
        subcategories = []
        for cat in product.get("categories", []):
            if str(cat["id"]) in categories_map:
                cat_info = categories_map[str(cat["id"])]
                product_categories.append(cat_info["name"])
                if cat_info["parent_id"] != 0:
                    subcategories.append(cat_info["name"])
        
        # Descriptions
        raw_description = product.get("description", "")
        raw_short_description = product.get("short_description", "")
        
        clean_description = self.processor.clean_html_content(raw_description)
        clean_short_description = self.processor.clean_html_content(raw_short_description)
        
        # Images
        images = []
        for i, img in enumerate(product.get("images", [])):
            images.append(ProductImage(
                url=img["src"],
                alt_text=img.get("alt", name),
                is_primary=(i == 0),
                size=f"{img.get('width', 0)}x{img.get('height', 0)}"
            ))
        
        # Specifications
        specifications = self.processor.extract_specifications(clean_description)
        
        # Use cases
        primary_uses, secondary_uses = self.processor.extract_use_cases(clean_description)
        
        # Safety information
        safety_info = self.processor.extract_safety_requirements(clean_description)
        
        # Pricing
        try:
            daily_rate = float(product.get("price", 0))
        except (ValueError, TypeError):
            daily_rate = 0.0
        
        pricing = ProductPricing(
            daily_rate=daily_rate,
            weekly_rate=daily_rate * 5.5 if daily_rate > 0 else None,  # Typical weekly discount
            monthly_rate=daily_rate * 20 if daily_rate > 0 else None,  # Typical monthly discount
            currency="CAD"
        )
        
        # Availability
        stock_status = product.get("stock_status", "instock")
        availability = ProductAvailability(
            status="available" if stock_status == "instock" else "unavailable",
            quantity_available=product.get("stock_quantity", 1) or 1
        )
        
        # Keywords and search
        keywords = self.processor.generate_search_keywords(product, product_categories)
        search_tags = list(set(keywords + [tag["name"] for tag in product.get("tags", [])]))
        
        # Current timestamp
        current_time = datetime.now(timezone.utc).isoformat()
        
        return RentalProduct(
            id=product_id,
            sku=sku,
            name=name,
            slug=slug,
            categories=product_categories,
            subcategories=subcategories,
            
            short_description=clean_short_description,
            full_description=clean_description,
            technical_description="",  # Could be extracted from specifications
            
            images=images,
            video_urls=[],  # Could be extracted from description
            manual_urls=[], # Could be extracted from description
            
            specifications=specifications,
            dimensions={},  # Could be extracted from specifications
            power_source="",
            
            pricing=pricing,
            availability=availability,
            
            primary_use_cases=primary_uses,
            secondary_use_cases=secondary_uses,
            industries_served=["Construction", "Landscaping", "Home Improvement"],  # Default
            project_types=[],
            
            safety=safety_info,
            
            keywords=keywords,
            search_tags=search_tags,
            related_products=[],
            
            created_date=product.get("date_created", current_time),
            last_updated=product.get("date_modified", current_time),
            review_count=0,
            
            # Optional fields
            brand=None,  # Extract from name if needed
            model=None,   # Extract from name if needed
            weight=None,
            popularity_score=0.0,
            review_rating=None
        )
    
    def fetch_all_data(self) -> MCPDataStructure:
        """Fetch all data and structure for MCP"""
        logger.info("Starting comprehensive data fetch...")
        
        # Get business info
        business_info = self._get_business_info()
        
        # Get categories
        categories_map = self._fetch_categories()
        
        # Get products
        products = []
        page = 1
        
        logger.info("Fetching WooCommerce products...")
        
        while True:
            try:
                products_response = self.wcapi.get("products", params={
                    "per_page": 100,
                    "page": page,
                    "status": "publish"
                }).json()
                
                if not products_response:
                    break
                
                for product in products_response:
                    try:
                        processed_product = self._process_product(product, categories_map)
                        products.append(processed_product)
                    except Exception as e:
                        logger.error(f"Error processing product {product.get('id', 'unknown')}: {e}")
                        continue
                
                page += 1
                logger.info(f"Processed page {page-1}, total products: {len(products)}")
                
            except Exception as e:
                logger.error(f"Error fetching products page {page}: {e}")
                break
        
        # Build search index
        search_index = self._build_search_index(products)
        
        # Create metadata
        metadata = {
            "version": "1.0.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_products": len(products),
            "total_categories": len(categories_map),
            "data_source": "WooCommerce API",
            "mcp_version": "0.3.0",
            "schema_version": "rental_equipment_v1.0"
        }
        
        # Operational data
        operational_data = {
            "last_sync": datetime.now(timezone.utc).isoformat(),
            "sync_status": "success",
            "data_quality_score": self._calculate_data_quality_score(products),
            "featured_products": [p.id for p in products[:5]],  # First 5 as featured
            "popular_categories": list(categories_map.keys())[:10]
        }
        
        return MCPDataStructure(
            metadata=metadata,
            business_info=business_info,
            product_catalog=products,
            categories=categories_map,
            search_index=search_index,
            operational_data=operational_data
        )
    
    def _build_search_index(self, products: List[RentalProduct]) -> Dict[str, List[str]]:
        """Build comprehensive search index"""
        search_index = {
            "by_category": {},
            "by_keyword": {},
            "by_use_case": {},
            "by_price_range": {}
        }
        
        for product in products:
            product_id = product.id
            
            # Index by category
            for category in product.categories:
                if category not in search_index["by_category"]:
                    search_index["by_category"][category] = []
                search_index["by_category"][category].append(product_id)
            
            # Index by keyword
            for keyword in product.keywords:
                if keyword not in search_index["by_keyword"]:
                    search_index["by_keyword"][keyword] = []
                search_index["by_keyword"][keyword].append(product_id)
            
            # Index by use case
            for use_case in product.primary_use_cases + product.secondary_use_cases:
                if use_case not in search_index["by_use_case"]:
                    search_index["by_use_case"][use_case] = []
                search_index["by_use_case"][use_case].append(product_id)
            
            # Index by price range
            price = product.pricing.daily_rate
            if price > 0:
                if price < 50:
                    price_range = "under_50"
                elif price < 100:
                    price_range = "50_to_100"
                elif price < 200:
                    price_range = "100_to_200"
                else:
                    price_range = "over_200"
                
                if price_range not in search_index["by_price_range"]:
                    search_index["by_price_range"][price_range] = []
                search_index["by_price_range"][price_range].append(product_id)
        
        return search_index
    
    def _calculate_data_quality_score(self, products: List[RentalProduct]) -> float:
        """Calculate data quality score"""
        if not products:
            return 0.0
        
        total_score = 0
        for product in products:
            score = 0
            
            # Check for essential fields
            if product.name: score += 1
            if product.short_description: score += 1
            if product.full_description: score += 1
            if product.images: score += 1
            if product.pricing.daily_rate > 0: score += 1
            if product.categories: score += 1
            if product.primary_use_cases: score += 1
            if product.specifications: score += 1
            
            total_score += score / 8  # Normalize to 0-1
        
        return total_score / len(products)
    
    def save_to_file(self, data: MCPDataStructure, output_path: str):
        """Save MCP data structure to JSON file"""
        try:
            # Convert dataclasses to dict
            data_dict = asdict(data)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save with proper formatting
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data_dict, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Successfully saved MCP data to {output_path}")
            logger.info(f"Total products: {len(data.product_catalog)}")
            logger.info(f"Data quality score: {data.operational_data['data_quality_score']:.2f}")
            
        except Exception as e:
            logger.error(f"Error saving data to {output_path}: {e}")
            raise

def main():
    """Main execution function"""
    try:
        fetcher = WooCommerceDataFetcher()
        mcp_data = fetcher.fetch_all_data()
        
        output_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'mcp_rental_catalog.json')
        fetcher.save_to_file(mcp_data, output_path)
        
        print(f"✅ Successfully generated MCP-compatible rental catalog")
        print(f"📊 Products: {len(mcp_data.product_catalog)}")
        print(f"📁 Categories: {len(mcp_data.categories)}")
        print(f"🎯 Data Quality: {mcp_data.operational_data['data_quality_score']:.1%}")
        
    except Exception as e:
        logger.error(f"Failed to generate MCP catalog: {e}")
        raise

if __name__ == "__main__":
    main()