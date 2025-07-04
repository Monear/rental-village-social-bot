
import os
import json
import logging
from datetime import datetime
from sanity import Client
from dotenv import load_dotenv
import uuid
from src.utils.sanity_asset_helpers import upload_image_to_sanity, create_sanity_image_object

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sanity client configuration
SANITY_PROJECT_ID = os.environ.get("SANITY_PROJECT_ID", "2pxuaj9k")
SANITY_DATASET = os.environ.get("SANITY_DATASET", "production")
SANITY_API_TOKEN = os.environ.get("SANITY_API_TOKEN") # Ensure this is set in your environment variables

sanity_client = Client(
    project_id=SANITY_PROJECT_ID,
    dataset=SANITY_DATASET,
    token=SANITY_API_TOKEN,
    use_cdn=False, # Use CDN for fresh data when writing
    logger=logger
)

def save_social_content_to_sanity(idea: dict) -> str | None:
    """
    Saves a generated social media content idea to Sanity.
    Returns the Sanity document ID if successful, None otherwise.
    """
    try:
        # Debug: Check what data we received
        print(f"📝 Processing content for Sanity: {idea.get('title', 'Unknown')}")
        if 'enhanced_images' in idea:
            print(f"   Enhanced images found: {len(idea['enhanced_images'])}")
        if 'enhanced_images_clean' in idea:
            print(f"   Clean images found: {len(idea['enhanced_images_clean'])}")
        
        # Check if the main idea object contains any bytes
        def check_for_bytes_in_idea(obj, path="idea"):
            if isinstance(obj, bytes):
                print(f"  🔍 Found bytes object in input at: {path}")
                return True
            elif isinstance(obj, dict):
                for key, value in obj.items():
                    if check_for_bytes_in_idea(value, f"{path}.{key}"):
                        return True
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    if check_for_bytes_in_idea(item, f"{path}[{i}]"):
                        return True
            return False
        
        check_for_bytes_in_idea(idea)
        
        # Store original enhanced images before cleaning (they contain the binary data we need)
        original_enhanced_images = idea.get("enhanced_images", [])
        
        # Create a clean copy of idea without binary data to prevent JSON serialization errors
        clean_idea = {}
        for key, value in idea.items():
            # Exclude binary data fields from final document
            if key in ['optimized_images', 'image_generation_summary']:
                continue  # Skip these binary data fields
            elif key == 'enhanced_images':
                # Keep enhanced_images structure but we'll process the original binary data separately
                clean_idea[key] = value
            elif key == 'enhanced_images_clean':
                continue  # Skip this, we'll use enhanced_images
            else:
                clean_idea[key] = value
        
        # Use clean_idea for processing
        idea = clean_idea
        print(f"  🧹 Using cleaned data structure for Sanity (preserved enhanced_images)")
        
        # Convert equipment data to Sanity references
        equipment_references = []
        if idea.get("related_equipment"):
            for equipment in idea["related_equipment"]:
                if equipment.get("_id"):
                    equipment_references.append({
                        "_type": "reference",
                        "_ref": equipment["_id"]
                    })

        # Process enhanced images (primary method) or fallback to equipment images
        image_objects = []
        
        # Use the original enhanced images (with binary data) for processing
        enhanced_images = original_enhanced_images
        if enhanced_images:
            print(f"📸 Processing {len(enhanced_images)} enhanced images for Sanity upload...")
            
            for i, enhanced_img in enumerate(enhanced_images):
                try:
                    # Handle enhanced images with binary data
                    if enhanced_img.get('image_data'):
                        # Save binary data to temporary file with proper format handling
                        import tempfile
                        import base64
                        
                        image_data = enhanced_img['image_data']
                        
                        # Debug: Log image data type and size
                        print(f"  🔍 Image {i+1} data type: {type(image_data)}")
                        if hasattr(image_data, '__len__'):
                            print(f"  🔍 Image {i+1} data size: {len(image_data)} bytes")
                        
                        # Handle different data formats from Gemini API
                        if isinstance(image_data, str):
                            # If it's a string, it's likely base64 encoded
                            try:
                                image_data = base64.b64decode(image_data)
                            except Exception as e:
                                print(f"  ❌ Error decoding base64 image data: {e}")
                                continue
                        elif hasattr(image_data, 'decode'):
                            # If it has a decode method, it might be bytes that need decoding
                            try:
                                # Try to decode as base64 first
                                image_data = base64.b64decode(image_data.decode())
                            except:
                                # If base64 decode fails, use as-is
                                image_data = image_data
                        
                        # Validate image data before writing
                        if not image_data or len(image_data) < 100:
                            print(f"  ❌ Image {i+1} data too small or empty ({len(image_data) if image_data else 0} bytes)")
                            continue
                        
                        # Convert to proper image format using PIL
                        from PIL import Image
                        import io
                        
                        # Load the image data and convert to PNG
                        try:
                            image = Image.open(io.BytesIO(image_data))
                            # Convert to RGB if needed (removes alpha channel issues)
                            if image.mode != 'RGB':
                                image = image.convert('RGB')
                            
                            # Save as PNG to temporary file
                            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                                image.save(temp_file, 'PNG')
                                temp_path = temp_file.name
                                
                        except Exception as e:
                            print(f"  ❌ Error converting image {i+1} format: {e}")
                            continue
                        
                        # Validate the file was written correctly
                        if not os.path.exists(temp_path) or os.path.getsize(temp_path) == 0:
                            print(f"  ❌ Failed to write image {i+1} to temporary file")
                            continue
                        
                        print(f"  📁 Wrote image {i+1} to temp file: {os.path.getsize(temp_path)} bytes")
                        
                        # Try uploading to Sanity with JPEG format instead  
                        # Convert to JPEG which Sanity prefers
                        try:
                            image = Image.open(io.BytesIO(image_data))
                            if image.mode != 'RGB':
                                image = image.convert('RGB')
                            
                            # Save as JPEG instead of PNG
                            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as jpeg_file:
                                image.save(jpeg_file, 'JPEG', quality=95)
                                jpeg_path = jpeg_file.name
                                
                            print(f"  📁 Converted image {i+1} to JPEG: {os.path.getsize(jpeg_path)} bytes")
                            
                            # Upload JPEG to Sanity
                            asset_result = upload_image_to_sanity(jpeg_path)
                            if asset_result:
                                image_obj = create_sanity_image_object(
                                    asset_data=asset_result,
                                    alt_text=enhanced_img.get('alt_text', f"Enhanced image {i+1}"),
                                    caption=enhanced_img.get('caption', enhanced_img.get('equipment_name', 'Equipment'))
                                )
                                image_objects.append(image_obj)
                                print(f"  ✅ Uploaded enhanced image {i+1}: {enhanced_img.get('equipment_name', 'Unknown')}")
                            else:
                                print(f"  ❌ Failed to upload enhanced image {i+1}")
                            
                            # Clean up temp files
                            os.unlink(temp_path)
                            os.unlink(jpeg_path)
                            
                        except Exception as jpeg_error:
                            print(f"  ❌ Error converting to JPEG: {jpeg_error}")
                            # Clean up temp file
                            os.unlink(temp_path)
                    
                    # Handle enhanced images with URLs (fallback to original)
                    elif enhanced_img.get('url'):
                        image_obj = create_sanity_image_object(
                            asset_data=enhanced_img['url'],
                            alt_text=enhanced_img.get('alt_text', f"Enhanced image {i+1}"),
                            caption=enhanced_img.get('caption', enhanced_img.get('equipment_name', 'Equipment'))
                        )
                        image_objects.append(image_obj)
                        print(f"  ✅ Using enhanced image URL {i+1}: {enhanced_img.get('equipment_name', 'Unknown')}")
                
                except Exception as e:
                    print(f"  ❌ Error processing enhanced image {i+1}: {e}")
        
        # Fallback to equipment images (legacy method)
        elif idea.get("equipment_images", []):
            equipment_images = idea.get("equipment_images", [])
            print(f"📸 Using {len(equipment_images)} equipment images (fallback method)...")
            
            for img in equipment_images:
                image_obj = create_sanity_image_object(
                    asset_data=img['url'],
                    alt_text=img['alt_text'],
                    caption=img['caption']
                )
                image_objects.append(image_obj)
        
        if image_objects:
            print(f"✅ Prepared {len(image_objects)} images for Sanity content")
        else:
            print("⚠️  No images found to add to Sanity content")

        # Remove binary data from enhanced_images for the final document
        if idea.get("enhanced_images"):
            clean_enhanced_images = []
            for img in idea["enhanced_images"]:
                clean_img = {k: v for k, v in img.items() if k != 'image_data'}
                clean_enhanced_images.append(clean_img)
            idea["enhanced_images"] = clean_enhanced_images
        
        # Map the idea dictionary to the Sanity socialContent schema
        sanity_document = {
            "_type": "socialContent",
            "_id": str(uuid.uuid4()), # Generate a unique ID
            "title": idea.get("title"),
            "body": idea.get("body"),
            "content_pillar": idea.get("content_pillar", "general_content"),
            "keywords": idea.get("keywords", ""),
            "platform": idea.get("platform", "Multi-platform"),
            "status": "generated",
            "performance_metrics": {},
            "images": image_objects,
            "related_equipment": equipment_references,
            "ai_generation_metadata": {
                "model_used": "gemini-1.5-flash",
                "temperature": 0.7,
                "timestamp": datetime.now().isoformat()
            },
        }
        
        # Debug: Check for any bytes objects before JSON serialization
        def check_for_bytes(obj, path=""):
            if isinstance(obj, bytes):
                print(f"  🔍 Found bytes object at: {path}")
                return True
            elif isinstance(obj, dict):
                for key, value in obj.items():
                    if check_for_bytes(value, f"{path}.{key}"):
                        return True
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    if check_for_bytes(item, f"{path}[{i}]"):
                        return True
            return False
        
        if check_for_bytes(sanity_document):
            print("  ❌ Document contains bytes objects that will cause JSON serialization errors")
        else:
            print("  ✅ Document is clean for JSON serialization")

        # Use createOrReplace to handle potential re-runs or updates
        transactions = [{'createOrReplace': sanity_document}]
        result = sanity_client.mutate(transactions=transactions)
        logger.info(f"Sanity mutate result for social content: {json.dumps(result, indent=2)}")
        
        # Debugging: Print the full result structure
        logger.info(f"Full mutate result structure: {result}")

        if result and result.get('results') and result['results'][0].get('operation') in ['create', 'update']:
            doc_id = sanity_document['_id'] # Use the ID generated earlier
            logger.info(f"Successfully saved social content to Sanity with ID: {doc_id}")
            return doc_id
        else:
            logger.error(f"Failed to save social content to Sanity: Unexpected result structure or operation: {result}")
            return None

    except Exception as e:
        logger.error(f"Error saving social content to Sanity: {e}")
        return None
