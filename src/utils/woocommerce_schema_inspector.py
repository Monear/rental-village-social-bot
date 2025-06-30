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

def inspect_woocommerce_schema(num_products=5):
    if not all([WOO_COMMERCE_URL, WOO_COMMERCE_CONSUMER_KEY, WOO_COMMERCE_CONSUMER_SECRET]):
        raise ValueError("WooCommerce API credentials (URL, CONSUMER_KEY, CONSUMER_SECRET) must be set in the .env file.")

    wcapi = API(
        url=WOO_COMMERCE_URL,
        consumer_key=WOO_COMMERCE_CONSUMER_KEY,
        consumer_secret=WOO_COMMERCE_CONSUMER_SECRET,
        version="wc/v3"
    )

    print(f"Fetching {num_products} sample products from WooCommerce to inspect their schema...")
    try:
        products_response = wcapi.get("products", params={
            "per_page": num_products,
            "status": "publish" # Only inspect published products
        })
        
        # Check if the response is successful before trying to parse JSON
        if products_response.status_code != 200:
            print(f"Error fetching products. Status Code: {products_response.status_code}")
            print(f"Response Body: {products_response.text}")
            return

        products_data = products_response.json()

        if not products_data:
            print("No products found or unable to fetch products. Please check your WooCommerce URL and API credentials.")
            return

        for i, product in enumerate(products_data):
            print(f"\n--- Product {i+1} (ID: {product.get('id')}, Name: {product.get('name')}) ---")
            print(json.dumps(product, indent=2))
            print("------------------------------------------------------------------")

        print("\nSchema inspection complete. Review the output above to identify relevant fields for 'use_cases', 'features', and 'image_keywords'.")

    except Exception as e:
        print(f"Error inspecting WooCommerce schema: {e}")
        print("Please ensure your WooCommerce URL and API credentials are correct and have sufficient permissions.")

if __name__ == "__main__":
    inspect_woocommerce_schema(num_products=3) # You can change the number of products to inspect