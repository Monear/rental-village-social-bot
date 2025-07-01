import os
import pytest
from unittest.mock import patch, MagicMock
from src.main import main, get_approved_content, post_to_social_media, update_notion_status

# Mock environment variables
@pytest.fixture(autouse=True)
def mock_env_vars():
    with patch.dict(os.environ, {
        "NOTION_TOKEN": "fake_notion_token",
        "DATABASE_ID": "fake_db_id",
    }):
        yield

# Mock Notion client
@pytest.fixture
def mock_notion_client():
    with patch('notion_client.Client') as mock_client:
        mock_notion = MagicMock()
        mock_client.return_value = mock_notion
        yield mock_notion

# Test get_approved_content
def test_get_approved_content_success(mock_notion_client):
    mock_notion_client.databases.query.return_value = {
        "results": [
            {"id": "page1", "properties": {"Copy": {"rich_text": [{"text": {"content": "Content 1"}}]}}},
            {"id": "page2", "properties": {"Copy": {"rich_text": [{"text": {"content": "Content 2"}}]}}}
        ]
    }
    content = get_approved_content()
    assert len(content) == 2
    assert content[0]['id'] == "page1"

def test_get_approved_content_no_content(mock_notion_client):
    mock_notion_client.databases.query.return_value = {"results": []}
    content = get_approved_content()
    assert len(content) == 0

def test_get_approved_content_missing_env_vars():
    with patch.dict(os.environ, {"NOTION_TOKEN": ""}),\
         pytest.raises(ValueError, match="NOTION_TOKEN and DATABASE_ID must be set in the .env file."): 
        get_approved_content()

# Test post_to_social_media (placeholder function)
def test_post_to_social_media():
    with patch('builtins.print') as mock_print:
        post_to_social_media("Test content")
        mock_print.assert_called_with("Posting to social media: Test content")

# Test update_notion_status
def test_update_notion_status_success(mock_notion_client):
    update_notion_status("page123")
    mock_notion_client.pages.update.assert_called_once_with(
        page_id="page123",
        properties={
            "Status": {
                "select": {
                    "name": "Posted"
                }
            }
        }
    )

# Test main function
def test_main_success(mock_notion_client):
    mock_notion_client.databases.query.return_value = {
        "results": [
            {"id": "page1", "properties": {"Copy": {"rich_text": [{"text": {"content": "Content 1"}}]}}}
        ]
    }
    with patch('src.main.post_to_social_media') as mock_post_social_media:
        with patch('src.main.update_notion_status') as mock_update_notion_status:
            with patch('builtins.print') as mock_print:
                main()
        mock_post_social_media.assert_called_once_with("Content 1")
        mock_update_notion_status.assert_called_once_with("page1")

def test_main_no_approved_content(mock_notion_client):
    mock_notion_client.databases.query.return_value = {"results": []}
    with patch('src.main.post_to_social_media') as mock_post_social_media,
         patch('src.main.update_notion_status') as mock_update_notion_status,
         patch('builtins.print') as mock_print:
        main()
        mock_post_social_media.assert_not_called()
        mock_update_notion_status.assert_not_called()

def test_main_content_property_missing(mock_notion_client):
    mock_notion_client.databases.query.return_value = {
        "results": [
            {"id": "page1", "properties": {}} # Missing 'Copy' property
        ]
    }
    with patch('src.main.post_to_social_media') as mock_post_social_media,
         patch('src.main.update_notion_status') as mock_update_notion_status,
         patch('builtins.print') as mock_print:
        main()
        mock_post_social_media.assert_not_called()
        mock_update_notion_status.assert_not_called()
        mock_print.assert_any_call("Warning: No content found for page page1")

def test_main_exception_handling(mock_notion_client):
    mock_notion_client.databases.query.return_value = {
        "results": [
            {"id": "page1", "properties": {"Copy": {"rich_text": [{"text": {"content": "Content 1"}}]}}}
        ]
    }
    with patch('src.main.post_to_social_media', side_effect=Exception("Posting error")),
         patch('builtins.print') as mock_print:
        main()
        mock_print.assert_any_call("Error processing item page1: Posting error")
