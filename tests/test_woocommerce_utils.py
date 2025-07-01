import os
import json
import pytest
from unittest.mock import patch, MagicMock, mock_open
from src.utils.woocommerce_data_pull import fetch_woocommerce_data
from src.utils.woocommerce_schema_inspector import inspect_woocommerce_schema

# Mock environment variables for testing
@pytest.fixture(autouse=True)
def mock_env_vars():
    with patch.dict(os.environ, {
        "WOO_COMMERCE_URL": "http://mock-woocommerce.com",
        "WOO_COMMERCE_CONSUMER_KEY": "mock_key",
        "WOO_COMMERCE_CONSUMER_SECRET": "mock_secret",
    }):
        yield

# Mock WooCommerce API responses
@pytest.fixture
def mock_wcapi_success():
    with patch('woocommerce.api.API.get') as mock_get:
        mock_get.side_effect = [
            # Categories response
            MagicMock(status_code=200, json=lambda: [
                {"id": 1, "name": "Category A"},
                {"id": 2, "name": "Category B"}
            ]),
            # Products response - Page 1
            MagicMock(status_code=200, json=lambda: [
                {
                    "id": 101,
                    "name": "Product 1",
                    "categories": [{"id": 1}],
                    "tags": [{"name": "tag1"}, {"name": "tag2"}],
                    "description": "<p>Description 1</p>",
                    "short_description": "<p>Short Desc 1</p>",
                    "images": [{"src": "http://img1.com/1.jpg"}],
                    "price": "10.00",
                    "sku": "SKU001",
                    "status": "publish"
                }
            ]),
            # Products response - Page 2 (empty to signal end)
            MagicMock(status_code=200, json=lambda: [])
        ]
        yield mock_get

@pytest.fixture
def mock_wcapi_empty_products():
    with patch('woocommerce.api.API.get') as mock_get:
        mock_get.side_effect = [
            # Categories response
            MagicMock(status_code=200, json=lambda: [
                {"id": 1, "name": "Category A"}
            ]),
            # Products response - Page 1 (empty)
            MagicMock(status_code=200, json=lambda: [])
        ]
        yield mock_get

@pytest.fixture
def mock_wcapi_auth_error():
    with patch('woocommerce.api.API.get') as mock_get:
        mock_get.return_value = MagicMock(status_code=401, text='{"code":"woocommerce_rest_authentication_error"}')
        yield mock_get

# Tests for fetch_woocommerce_data
def test_fetch_woocommerce_data_success(mock_wcapi_success):
    mock_output_path = "src/data/machine_context.json"
    with patch('builtins.open', mock_open()) as mocked_file_open:
        with patch('json.dump') as mocked_json_dump:
            with patch('builtins.print') as mocked_print:
                fetch_woocommerce_data()
        
        mocked_file_open.assert_called_once_with(mock_output_path, 'w')
        mocked_json_dump.assert_called_once()
        args, kwargs = mocked_json_dump.call_args
        generated_data = args[0]
        
        assert "business_info" in generated_data
        assert len(generated_data["available_machines"]) == 1
        assert generated_data["available_machines"][0]["name"] == "Product 1"
        assert generated_data["available_machines"][0]["category"] == "Category A"
        assert "tag1" in generated_data["available_machines"][0]["image_keywords"]
        assert "tag2" in generated_data["available_machines"][0]["image_keywords"]
        assert generated_data["available_machines"][0]["description"] == "Description 1"
        assert generated_data["available_machines"][0]["short_description"] == "Short Desc 1"
        mocked_print.assert_called_with(f"Successfully updated {mock_output_path} with WooCommerce data.")

def test_fetch_woocommerce_data_empty_products(mock_wcapi_empty_products):
    mock_output_path = "src/data/machine_context.json"
    with patch('builtins.open', mock_open()) as mocked_file_open,
         patch('json.dump') as mocked_json_dump,
         patch('builtins.print') as mocked_print:
        
        fetch_woocommerce_data()
        
        mocked_file_open.assert_called_once_with(mock_output_path, 'w')
        mocked_json_dump.assert_called_once()
        args, kwargs = mocked_json_dump.call_args
        generated_data = args[0]
        
        assert len(generated_data["available_machines"]) == 0
        mocked_print.assert_called_with(f"Successfully updated {mock_output_path} with WooCommerce data.")

def test_fetch_woocommerce_data_missing_env_vars():
    with patch.dict(os.environ, {
        "WOO_COMMERCE_URL": "",
        "WOO_COMMERCE_CONSUMER_KEY": "mock_key",
        "WOO_COMMERCE_CONSUMER_SECRET": "mock_secret",
    }):
        with pytest.raises(ValueError, match="WooCommerce API credentials"): 
            fetch_woocommerce_data()

# Tests for inspect_woocommerce_schema
def test_inspect_woocommerce_schema_success(mock_wcapi_success):
    with patch('builtins.print') as mocked_print:
        inspect_woocommerce_schema(num_products=1)
        # Assert that product details are printed
        mocked_print.assert_any_call(f"\n--- Product 1 (ID: 101, Name: Product 1) ---")
        mocked_print.assert_any_call(json.dumps({
            "id": 101,
            "name": "Product 1",
            "categories": [{"id": 1}],
            "tags": [{"name": "tag1"}, {"name": "tag2"}],
            "description": "<p>Description 1</p>",
            "short_description": "<p>Short Desc 1</p>",
            "images": [{"src": "http://img1.com/1.jpg"}],
            "price": "10.00",
            "sku": "SKU001",
            "status": "publish"
        }, indent=2))
        mocked_print.assert_any_call("Schema inspection complete. Review the output above to identify relevant fields for 'use_cases', 'features', and 'image_keywords'.")

def test_inspect_woocommerce_schema_empty_products(mock_wcapi_empty_products):
    with patch('builtins.print') as mocked_print:
        inspect_woocommerce_schema(num_products=1)
        mocked_print.assert_any_call("No products found or unable to fetch products. Please check your WooCommerce URL and API credentials.")

def test_inspect_woocommerce_schema_auth_error(mock_wcapi_auth_error):
    with patch('builtins.print') as mocked_print:
        inspect_woocommerce_schema(num_products=1)
        mocked_print.assert_any_call("Error fetching products. Status Code: 401")
        mocked_print.assert_any_call("Response Body: {\"code\":\"woocommerce_rest_authentication_error\"}")

def test_inspect_woocommerce_schema_missing_env_vars():
    with patch.dict(os.environ, {
        "WOO_COMMERCE_URL": "",
        "WOO_COMMERCE_CONSUMER_KEY": "mock_key",
        "WOO_COMMERCE_CONSUMER_SECRET": "mock_secret",
    }):
        with pytest.raises(ValueError, match="WooCommerce API credentials"): 
            inspect_woocommerce_schema()
