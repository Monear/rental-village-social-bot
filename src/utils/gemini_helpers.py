# utils/gemini_helpers.py
"""Helpers for interacting with the Gemini API."""
import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def generate_ideas_with_gemini(guidelines, num_ideas, user_input=None, existing_ideas=None):
    """Generates content ideas using the Gemini API (new google-genai SDK)."""
    if existing_ideas is None:
        existing_ideas = []

    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY must be set in the .env file.")

    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = f"""
    You are a creative social media manager for a tool rental company.
    Your task is to generate {num_ideas} fresh, engaging content ideas.
    Adhere strictly to the following Content Guidelines:
    ---
    {guidelines}
    ---
    """
    if user_input:
        prompt += f"Base your suggestions on this user-provided text:\n---\n{user_input}\n---\n"

    if existing_ideas:
        prompt += """
        IMPORTANT: Avoid generating ideas that are too similar to the following existing ideas. Focus on novelty and distinctiveness:
        ---
        """
        for i, idea in enumerate(existing_ideas):
            prompt += f"Idea {i+1}:\nTitle: {idea['title']}\nCopy: {idea['copy']}\n---\n"

    prompt += """
    For each idea, provide a content pillar, a short catchy title (under 100 chars), the full post body, and 3-5 relevant keywords for an image search.
    Return your response as a valid JSON array of objects. Each object must have "pillar", "title", "body", and "keywords" keys.
    Example:
    [
        {
            "pillar": "Tool Spotlight",
            "title": "Mini-Excavator: Small But Mighty",
            "body": "Check out this 15-second video on the versatility of our new mini-excavator. Perfect for tight spaces and big jobs! #ToolRental #Excavator",
            "keywords": "excavator, construction, digging, small space"
        }
    ]
    """
    print("Generating content ideas with Gemini...")
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )
        cleaned_response = response.candidates[0].content.parts[0].text.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned_response)
    except Exception as e:
        print(f"Error generating ideas with Gemini: {e}")
        if 'response' in locals():
            print(f"Raw response from API: {getattr(response, 'text', '')}")
        return []

def generate_image_with_gemini(prompt, output_path, num_images=3, instructions_path=None):
    """Generates up to num_images using Gemini (text-to-image) and saves them. Returns a list of file paths.
    If instructions_path is provided, loads the prompt instructions from that file and prepends them to the prompt."""
    try:
        from google.genai import types
        from PIL import Image
        from io import BytesIO
        import sys
        client = genai.Client(api_key=GEMINI_API_KEY)
        image_paths = []
        # Load instructions from .md file if provided
        instructions = None
        if instructions_path:
            try:
                with open(instructions_path, 'r') as f:
                    instructions = f.read().strip()
            except Exception as e:
                print(f"Warning: Could not read image generation instructions: {e}", file=sys.stderr)
        for i in range(num_images):
            full_prompt = ""
            if instructions:
                full_prompt += instructions + "\n\n"
            full_prompt += f"{prompt}\nVariation {i+1} of {num_images}."
            response = client.models.generate_content(
                model="gemini-2.0-flash-preview-image-generation",
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    response_modalities=['TEXT', 'IMAGE']
                )
            )
            found_image = False
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'inline_data') and part.inline_data is not None:
                    image = Image.open(BytesIO(part.inline_data.data))
                    variation_path = output_path.replace('.png', f'_v{i+1}.png')
                    image.save(variation_path)
                    image_paths.append(variation_path)
                    found_image = True
                    break
            if not found_image:
                print(f"No image generated for variation {i+1}.")
        return image_paths if image_paths else None
    except Exception as e:
        print(f"Error generating image with Gemini: {e}")
        return None
