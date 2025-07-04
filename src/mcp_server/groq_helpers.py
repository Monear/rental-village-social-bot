
# src/mcp_server/groq_helpers.py

# This file will contain helper functions for common GROQ queries.
# Examples of functions that could be implemented here:
# - get_equipment_by_category(category_name)
# - get_active_prompts(prompt_type)
# - search_equipment_by_keyword(keyword)
# - get_latest_social_content(platform)

# These functions would encapsulate GROQ query logic, making it reusable and easier to manage.

# Example structure:
# from sanity import Client
# import os

# SANITY_PROJECT_ID = os.environ.get("SANITY_PROJECT_ID")
# SANITY_DATASET = os.environ.get("SANITY_DATASET")
# SANITY_API_TOKEN = os.environ.get("SANITY_API_TOKEN")

# client = Client(
#     project_id=SANITY_PROJECT_ID,
#     dataset=SANITY_DATASET,
#     token=SANITY_API_TOKEN,
#     use_cdn=True
# )

# def get_equipment_by_category(category_name):
#     query = f"*[_type == \"equipment\" && \"{category_name}\" in categories]"
#     return client.query(groq=query)
