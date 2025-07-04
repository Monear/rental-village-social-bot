#!/usr/bin/env python3
"""
Populate Default Configuration Data in Sanity
This script creates default configuration documents for the content strategy system.
"""

import os
import sys
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../../.env'), override=True)

from sanity import Client
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sanity client configuration
SANITY_PROJECT_ID = os.environ.get("SANITY_PROJECT_ID", "2pxuaj9k")
SANITY_DATASET = os.environ.get("SANITY_DATASET", "production")
SANITY_API_TOKEN = os.environ.get("SANITY_API_TOKEN")

if not SANITY_API_TOKEN:
    raise ValueError("SANITY_API_TOKEN must be set in the .env file.")

sanity_client = Client(
    project_id=SANITY_PROJECT_ID,
    dataset=SANITY_DATASET,
    token=SANITY_API_TOKEN,
    use_cdn=False,  # Use write API, not CDN
    logger=logger
)

def create_default_content_strategy():
    """Create default content strategy configuration"""
    
    content_strategy = {
        "_type": "contentStrategy",
        "_id": str(uuid.uuid4()),
        "title": "Default Content Strategy 2024",
        "active": True,
        "pillarWeights": {
            "equipmentSpotlight": 0.3,
            "seasonalContent": 0.25,
            "projectShowcase": 0.2,
            "safetyTraining": 0.15,
            "educationalContent": 0.1
        },
        "platformPreferences": {
            "facebook": 40,
            "instagram": 35,
            "blog": 25
        },
        "equipmentSelectionRules": {
            "prioritizeNewEquipment": True,
            "prioritizeUnderutilized": True,
            "prioritizeHighMargin": False,
            "excludeUnavailable": True,
            "maxEquipmentAge": 365
        },
        "contentQualityRules": {
            "minImageQuality": 7,
            "requireEquipmentImages": True,
            "maxContentLength": {
                "facebook": 2000,
                "instagram": 2200,
                "blog": 1500
            },
            "minContentLength": {
                "facebook": 100,
                "instagram": 125,
                "blog": 300
            }
        },
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat()
    }
    
    return content_strategy

def create_default_seasonal_settings():
    """Create default seasonal settings configuration"""
    
    seasonal_settings = {
        "_type": "seasonalSettings",
        "_id": str(uuid.uuid4()),
        "title": "Current Seasonal Settings",
        "active": True,
        "currentSeason": "winter",  # Update based on current season
        "seasonalKeywords": {
            "spring": ["spring", "landscaping", "gardening", "planting", "cleanup", "preparation"],
            "summer": ["summer", "construction", "outdoor", "hot weather", "irrigation", "maintenance"],
            "fall": ["fall", "autumn", "harvest", "leaf removal", "preparation", "winterizing"],
            "winter": ["winter", "snow", "cold", "ice", "heating", "indoor projects"]
        },
        "seasonalEquipmentPriority": {
            "spring": ["landscaping", "excavation", "lawn-care", "compaction", "material-handling"],
            "summer": ["construction", "concrete", "demolition", "pumps", "generators"],
            "fall": ["leaf-blowers", "chippers", "excavation", "landscaping", "cleanup"],
            "winter": ["snow-removal", "heaters", "indoor-tools", "pumps", "generators"]
        },
        "seasonalContentThemes": {
            "spring": ["Spring Preparation", "Landscaping Projects", "Clean-up Time", "Garden Ready"],
            "summer": ["Summer Projects", "Beat the Heat", "Outdoor Work", "Construction Season"],
            "fall": ["Fall Cleanup", "Harvest Time", "Winter Prep", "Leaf Season"],
            "winter": ["Winter Solutions", "Snow Management", "Indoor Projects", "Cold Weather Tools"]
        },
        "seasonalBoosts": {
            "currentSeasonBoost": 2.0,
            "upcomingSeasonBoost": 1.5,
            "offSeasonPenalty": 0.3
        },
        "weatherConsiderations": {
            "temperatureRanges": {
                "spring": {"min": 45, "max": 75},
                "summer": {"min": 70, "max": 95},
                "fall": {"min": 40, "max": 70},
                "winter": {"min": 20, "max": 50}
            },
            "equipmentTemperatureRatings": True
        },
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat()
    }
    
    return seasonal_settings

def create_default_image_generation_settings():
    """Create default image generation settings"""
    
    image_settings = {
        "_type": "imageGenerationSettings",
        "_id": str(uuid.uuid4()),
        "title": "Default Image Generation Settings",
        "active": True,
        "brandGuidelines": {
            "brandColors": [
                {"name": "Primary Blue", "hex": "#1E40AF", "usage": "Main brand color"},
                {"name": "Secondary Orange", "hex": "#F59E0B", "usage": "Accent color"},
                {"name": "Neutral Gray", "hex": "#6B7280", "usage": "Text and backgrounds"}
            ],
            "logoUsage": "Always include the Rental Village logo in the bottom right corner. Maintain clear space around the logo equal to the height of the logo.",
            "fontPreferences": ["Arial Bold", "Helvetica", "Sans-serif"],
            "visualStyle": "professional"
        },
        "imageEnhancementPrompts": {
            "equipmentSpotlight": "Enhance this equipment image with professional lighting, clean background, and dynamic positioning. Add subtle brand colors and ensure the equipment is the focal point. Make it look premium and well-maintained.",
            "projectShowcase": "Show this equipment in action on a realistic job site. Add appropriate scenery, other complementary equipment, and workers if relevant. Make it look like a successful, professional project in progress.",
            "seasonalContent": "Enhance this equipment image with appropriate seasonal elements. Add weather conditions, seasonal landscapes, and contextual details that match the current season. Ensure the equipment looks ready for seasonal challenges.",
            "safetyTraining": "Emphasize safety features of this equipment. Add safety equipment, proper operator attire, warning signs, and safety-focused visual elements. Make safety the prominent theme while showcasing the equipment.",
            "educationalContent": "Create an educational diagram or infographic style image highlighting key features of this equipment. Add labels, specifications, and visual callouts that help explain how the equipment works."
        },
        "imageQualityStandards": {
            "minResolution": {"width": 1080, "height": 1080},
            "preferredAspectRatios": {
                "facebook": "1:1",
                "instagram": "1:1", 
                "blog": "16:9"
            },
            "imageFormats": ["PNG", "JPEG", "WebP"],
            "maxFileSize": 10
        },
        "generationRules": {
            "maxImagesPerPost": 3,
            "fallbackToOriginal": True,
            "requireEquipmentVisibility": True,
            "includeWatermark": True,
            "watermarkPosition": "bottom-right"
        },
        "safetyFilters": {
            "prohibitedElements": [
                "unsafe working conditions",
                "missing safety equipment", 
                "inappropriate attire",
                "dangerous operations",
                "unsecured equipment"
            ],
            "requiredSafetyElements": [
                "proper safety equipment",
                "professional operators",
                "secure equipment positioning",
                "clear warning signs",
                "safe operating distances"
            ],
            "automaticSafetyCheck": True
        },
        "performanceSettings": {
            "maxGenerationTime": 60,
            "retryAttempts": 3,
            "batchSize": 1
        },
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat()
    }
    
    return image_settings

def create_default_platform_settings():
    """Create default platform-specific settings"""
    
    platform_settings = {
        "_type": "platformSettings",
        "_id": str(uuid.uuid4()),
        "title": "Default Platform Settings",
        "active": True,
        "facebook": {
            "enabled": True,
            "contentStyle": {
                "tone": "professional",
                "callToAction": "soft"
            },
            "contentLength": {
                "min": 100,
                "max": 2000,
                "optimal": 500
            },
            "imageSpecs": {
                "width": 1200,
                "height": 630,
                "aspectRatio": "1.91:1",
                "maxImages": 10
            },
            "hashtags": {
                "maxHashtags": 30,
                "optimalHashtags": 5,
                "placement": "end"
            },
            "postingSchedule": {
                "frequency": "every-2-days",
                "optimalTimes": ["9:00 AM", "1:00 PM", "3:00 PM", "5:00 PM"]
            }
        },
        "instagram": {
            "enabled": True,
            "contentStyle": {
                "tone": "casual",
                "emojiUsage": "moderate"
            },
            "contentLength": {
                "min": 125,
                "max": 2200,
                "optimal": 400
            },
            "imageSpecs": {
                "width": 1080,
                "height": 1080,
                "aspectRatio": "1:1",
                "maxImages": 10
            },
            "hashtags": {
                "maxHashtags": 30,
                "optimalHashtags": 15,
                "placement": "end"
            },
            "postingSchedule": {
                "frequency": "daily",
                "optimalTimes": ["11:00 AM", "1:00 PM", "5:00 PM", "7:00 PM"]
            }
        },
        "blog": {
            "enabled": True,
            "contentStyle": {
                "tone": "educational",
                "structure": "how-to"
            },
            "contentLength": {
                "min": 300,
                "max": 1500,
                "optimal": 800
            },
            "imageSpecs": {
                "width": 1200,
                "height": 675,
                "aspectRatio": "16:9",
                "maxImages": 5
            },
            "seoSettings": {
                "titleLength": 60,
                "metaDescriptionLength": 160,
                "keywordDensity": 2,
                "includeTableOfContents": True
            },
            "postingSchedule": {
                "frequency": "weekly",
                "optimalTimes": ["10:00 AM", "2:00 PM"]
            }
        },
        "crossPlatformSettings": {
            "allowRepurposing": True,
            "adaptationRules": [
                {
                    "rule": "Length Adjustment",
                    "description": "Automatically adjust content length to fit platform requirements"
                },
                {
                    "rule": "Hashtag Optimization", 
                    "description": "Optimize hashtag count and placement for each platform"
                },
                {
                    "rule": "Image Resizing",
                    "description": "Resize images to optimal dimensions for each platform"
                }
            ],
            "brandConsistency": [
                "Maintain consistent brand voice across all platforms",
                "Use consistent visual style and branding elements",
                "Ensure equipment safety standards are always highlighted",
                "Include rental contact information in all posts"
            ]
        },
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat()
    }
    
    return platform_settings

def populate_all_defaults():
    """Populate all default configuration documents"""
    
    print("🚀 Starting population of default configuration data...")
    
    documents_to_create = [
        ("Content Strategy", create_default_content_strategy()),
        ("Seasonal Settings", create_default_seasonal_settings()),
        ("Image Generation Settings", create_default_image_generation_settings()),
        ("Platform Settings", create_default_platform_settings())
    ]
    
    created_documents = []
    
    for doc_name, doc_data in documents_to_create:
        try:
            print(f"\n📝 Creating {doc_name}...")
            
            # Check if document already exists
            existing = sanity_client.query(
                f'*[_type == "{doc_data["_type"]}" && active == true][0]'
            )
            
            if existing.get('result'):
                print(f"   ⚠️  Active {doc_name} already exists. Skipping creation.")
                print(f"   📋 Existing document ID: {existing['result']['_id']}")
                continue
            
            # Create the document using mutate
            mutations = [
                {
                    "create": doc_data
                }
            ]
            
            result = sanity_client.mutate(mutations)
            if result and result.get('results'):
                doc_id = doc_data['_id']
                created_documents.append((doc_name, {'_id': doc_id}))
            else:
                raise Exception(f"Failed to create document: {result}")
            
            print(f"   ✅ {doc_name} created successfully!")
            print(f"   📋 Document ID: {doc_id}")
            
        except Exception as e:
            print(f"   ❌ Failed to create {doc_name}: {e}")
            logger.error(f"Error creating {doc_name}: {e}")
    
    print(f"\n🎉 Population complete! Created {len(created_documents)} documents:")
    for doc_name, result in created_documents:
        print(f"   - {doc_name}: {result['_id']}")
    
    print(f"\n📊 Summary:")
    print(f"   - Total documents processed: {len(documents_to_create)}")
    print(f"   - Successfully created: {len(created_documents)}")
    print(f"   - Skipped (already exist): {len(documents_to_create) - len(created_documents)}")
    
    print(f"\n🌐 You can now view and edit these configurations in Sanity Studio at:")
    print(f"   http://localhost:3333")

def verify_configuration():
    """Verify that all configuration documents are properly set up"""
    
    print("\n🔍 Verifying configuration setup...")
    
    config_types = [
        ("contentStrategy", "Content Strategy"),
        ("seasonalSettings", "Seasonal Settings"), 
        ("imageGenerationSettings", "Image Generation Settings"),
        ("platformSettings", "Platform Settings")
    ]
    
    all_good = True
    
    for doc_type, display_name in config_types:
        try:
            result = sanity_client.query(f'*[_type == "{doc_type}" && active == true]')
            active_configs = result.get('result', [])
            
            if len(active_configs) == 0:
                print(f"   ❌ No active {display_name} found")
                all_good = False
            elif len(active_configs) == 1:
                print(f"   ✅ {display_name}: 1 active configuration")
            else:
                print(f"   ⚠️  {display_name}: {len(active_configs)} active configurations (should be 1)")
                all_good = False
                
        except Exception as e:
            print(f"   ❌ Error checking {display_name}: {e}")
            all_good = False
    
    if all_good:
        print("\n🎉 All configurations are properly set up!")
    else:
        print("\n⚠️  Some configuration issues detected. Please review and fix.")
    
    return all_good

def main():
    """Main execution function"""
    
    print("🏗️  Rental Village Content Strategy Configuration Setup")
    print("="*60)
    
    # Populate default configurations
    populate_all_defaults()
    
    # Verify setup
    verify_configuration()
    
    print("\n" + "="*60)
    print("🏁 Configuration setup complete!")
    print("\nNext steps:")
    print("1. Open Sanity Studio at http://localhost:3333")
    print("2. Navigate to ⚙️ Configuration & Settings")
    print("3. Review and customize the default settings")
    print("4. Update suggest_content.py to use the new configuration system")

if __name__ == "__main__":
    main()