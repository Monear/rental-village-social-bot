import os
import json
from woocommerce import API
from dotenv import load_dotenv

# Load environment variables from the root .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

WOO_COMMERCE_URL = os.getenv("WOO_COMMERCE_URL")
WOO_COMMERCE_CONSUMER_KEY = os.getenv("WOO_COMMERCE_CONSUMER_KEY")
WOO_COMMERCE_CONSUMER_SECRET = os.getenv("WOO_COMMERCE_CONSUMER_SECRET")

def fetch_woocommerce_data():
    if not all([WOO_COMMERCE_URL, WOO_COMMERCE_CONSUMER_KEY, WOO_COMMERCE_CONSUMER_SECRET]):
        raise ValueError("WooCommerce API credentials (URL, CONSUMER_KEY, CONSUMER_SECRET) must be set in the .env file.")

    wcapi = API(
        url=WOO_COMMERCE_URL,
        consumer_key=WOO_COMMERCE_CONSUMER_KEY,
        consumer_secret=WOO_COMMERCE_CONSUMER_SECRET,
        version="wc/v3"
    )

    machine_context = {
        "business_info": {
            "name": "Rental Village",
            "location": "Your City, State", # Update this if needed
            "slogan": "Your project, our tools.", # Update this if needed
            "contact_info": "rentals@rentalvillage.com | (555) 123-4567" # Update this if needed
        },
        "available_machines": [],
        "unavailable_machines": [] # You might populate this manually or based on stock status
    }

    print("Fetching WooCommerce categories...")
    categories_response = wcapi.get("products/categories", params={"per_page": 100}).json()
    categories_map = {cat["id"]: cat["name"] for cat in categories_response if "id" in cat and "name" in cat}

    print("Fetching WooCommerce products...")
    page = 1
    while True:
        products_response = wcapi.get("products", params={
            "per_page": 100, 
            "page": page,
            "status": "publish" # Only fetch published products
        }).json()
        
        if not products_response:
            break

        for product in products_response:
            product_categories = [categories_map.get(cat["id"]) for cat in product.get("categories", []) if cat["id"] in categories_map]
            product_tags = [tag["name"] for tag in product.get("tags", [])]
            
            # Assuming all published products are 'available machines'
            # You might want to add logic here to check stock_status if needed
            machine_context["available_machines"].append({
                "id": str(product["id"]),
                "name": product["name"],
                "category": ", ".join(product_categories) if product_categories else "Uncategorized",
                "description": product["description"].replace("<p>", "").replace("</p>", "").strip(), # Clean HTML tags
                "short_description": product["short_description"].replace("<p>", "").replace("</p>", "").strip(), # Clean HTML tags
                "images": [img["src"] for img in product.get("images", [])],
                "price": product["price"],
                "sku": product["sku"],
                "use_cases": [], # Populate manually or from product attributes if available
                "features": [], # Populate manually or from product attributes if available
                "image_keywords": product_tags # Populated from product tags
            })
        page += 1

    output_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'machine_context.json')
    with open(output_path, 'w') as f:
        json.dump(machine_context, f, indent=2)
    print(f"Successfully updated {output_path} with WooCommerce data.")

if __name__ == "__main__":
    fetch_woocommerce_data()