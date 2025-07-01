import os
import json
import pytest
from unittest.mock import patch, MagicMock
from src.utils.check_notion_db import main

# Mock environment variables
@pytest.fixture(autouse=True)
def mock_env_vars():
    with patch.dict(os.environ, {
        "NOTION_API_KEY": "fake_notion_key",
        "NOTION_DATABASE_ID": "fake_db_id",
    }):
        yield

# Mock Notion client
@pytest.fixture
def mock_notion_client():
    with patch('notion_client.Client') as mock_client:
        mock_notion = MagicMock()
        mock_client.return_value = mock_notion
        yield mock_notion

def test_main_success(mock_notion_client):
    mock_notion_client.databases.retrieve.return_value = {
        "properties": {
            "Name": {"type": "title"},
            "Post Date": {"type": "date"},
            "Content Pillar": {"type": "select", "select": {"options": [{"name": "Promotion"}, {"name": "Safety First"}]}}
        }
    }
    with patch('builtins.print') as mock_print:
        main()
        mock_notion_client.databases.retrieve.assert_called_once_with(database_id="fake_db_id")
        mock_print.assert_any_call("Fetching properties for database: fake_db_id")
        mock_print.assert_any_call("--- Database Properties ---")
        mock_print.assert_any_call("- Name: 'Name'")
        mock_print.assert_any_call("  Type: title")
        mock_print.assert_any_call("- Name: 'Content Pillar'")
        mock_print.assert_any_call("  Type: select")
        mock_print.assert_any_call("  Options: ['Promotion', 'Safety First']")
        mock_print.assert_any_call("-------------------------")

def test_main_missing_env_vars():
    with patch.dict(os.environ, {"NOTION_API_KEY": ""}),\
         pytest.raises(ValueError, match="NOTION_API_KEY and NOTION_DATABASE_ID must be set in the .env file."): 
        main()

def test_main_notion_api_error(mock_notion_client):
    mock_notion_client.databases.retrieve.side_effect = Exception("API Error")
    with patch('builtins.print') as mock_print:
        main()
        mock_print.assert_any_call("An error occurred: API Error")
