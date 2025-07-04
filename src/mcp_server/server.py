
from FastMCP import FastMCP
from mcp.resource import Resource
from mcp.tool import Tool
from mcp.prompt import Prompt
import os
import logging
from sanity import Client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sanity client configuration
SANITY_PROJECT_ID = os.environ.get("SANITY_PROJECT_ID", "ovHF0xC8j")
SANITY_DATASET = os.environ.get("SANITY_DATASET", "production")
SANITY_API_TOKEN = os.environ.get("SANITY_API_TOKEN") # Ensure this is set in your environment variables

sanity_client = Client(
    project_id=SANITY_PROJECT_ID,
    dataset=SANITY_DATASET,
    token=SANITY_API_TOKEN,
    use_cdn=True, # Use CDN for MCP server for faster reads
    logger=logger
)

app = FastMCP(
    title="Rental Village MCP Server",
    version="1.0.0",
    description="MCP Server for Rental Village, providing access to Sanity data and tools."
)

# Define Resources
@app.resource(
    name="equipment_catalog",
    description="Provides access to the Rental Village equipment catalog from Sanity."
)
async def get_equipment_catalog(query: str = "*[_type == \"equipment\"]"):
    """
    Fetches equipment data from Sanity using a GROQ query.
    Args:
        query (str): A GROQ query string to fetch equipment. Defaults to all equipment.
    """
    try:
        result = sanity_client.query(groq=query)
        return result
    except Exception as e:
        logger.error(f"Error fetching equipment catalog: {e}")
        return {"error": str(e)}

@app.resource(
    name="content_prompts",
    description="Provides access to AI content generation prompts from Sanity."
)
async def get_content_prompts(query: str = "*[_type == \"contentPrompt\"]"):
    """
    Fetches content prompts from Sanity using a GROQ query.
    Args:
        query (str): A GROQ query string to fetch prompts. Defaults to all prompts.
    """
    try:
        result = sanity_client.query(groq=query)
        return result
    except Exception as e:
        logger.error(f"Error fetching content prompts: {e}")
        return {"error": str(e)}

@app.resource(
    name="business_context",
    description="Provides access to Rental Village business context from Sanity."
)
async def get_business_context(query: str = "*[_type == \"businessContext\"]"):
    """
    Fetches business context from Sanity using a GROQ query.
    Args:
        query (str): A GROQ query string to fetch business context. Defaults to all business context documents.
    """
    try:
        result = sanity_client.query(groq=query)
        return result
    except Exception as e:
        logger.error(f"Error fetching business context: {e}")
        return {"error": str(e)}

# Define Tools (Placeholders for now)
@app.tool(
    name="generate_social_media_content",
    description="Generates social media content based on provided prompts and equipment data."
)
async def generate_social_media_content(prompt_id: str, equipment_id: str):
    """
    Placeholder for social media content generation logic.
    """
    return {"status": "success", "message": "Content generation not yet implemented."}

@app.tool(
    name="sync_content_to_notion",
    description="Synchronizes generated content to Notion."
)
async def sync_content_to_notion(content_id: str):
    """
    Placeholder for Notion synchronization logic.
    """
    return {"status": "success", "message": "Notion sync not yet implemented."}

# Define Prompts (Placeholders for now)
@app.prompt(
    name="suggest_content_idea",
    description="Suggests a new social media content idea based on available equipment and prompts."
)
async def suggest_content_idea(equipment_name: str):
    """
    Placeholder for content idea suggestion prompt.
    """
    return f"Please suggest a social media content idea for {equipment_name}."

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
