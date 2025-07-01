import os
import pytest
from unittest.mock import patch, MagicMock
from datetime import date, timedelta
from src.track_performance import main, get_posted_content_from_notion, get_performance_metrics, update_notion_with_metrics

# Mock environment variables
@pytest.fixture(autouse=True)
def mock_env_vars():
    with patch.dict(os.environ, {
        "NOTION_TOKEN": "fake_notion_token",
        "DATABASE_ID": "fake_db_id",
        "FACEBOOK_API_TOKEN": "fake_fb_token",
        "INSTAGRAM_API_TOKEN": "fake_ig_token",
    }):
        yield

# Mock Notion client
@pytest.fixture
def mock_notion_client():
    with patch('notion_client.Client') as mock_client:
        mock_notion = MagicMock()
        mock_client.return_value = mock_notion
        yield mock_notion

# Test get_posted_content_from_notion
def test_get_posted_content_from_notion_success(mock_notion_client):
    mock_notion_client.databases.query.return_value = {
        "results": [
            {"id": "page1", "properties": {"Platform": {"select": {"name": "Facebook"}}, "Post ID": {"rich_text": [{"text": {"content": "fb_post_1"}}]}}},
            {"id": "page2", "properties": {"Platform": {"select": {"name": "Instagram"}}, "Post ID": {"rich_text": [{"text": {"content": "ig_post_1"}}]}}}
        ]
    }
    posts = get_posted_content_from_notion(mock_notion_client)
    assert len(posts) == 2
    assert posts[0]['id'] == "page1"

def test_get_posted_content_from_notion_no_posts(mock_notion_client):
    mock_notion_client.databases.query.return_value = {"results": []}
    posts = get_posted_content_from_notion(mock_notion_client)
    assert len(posts) == 0

def test_get_posted_content_from_notion_exception(mock_notion_client):
    mock_notion_client.databases.query.side_effect = Exception("Notion error")
    with patch('builtins.print') as mock_print:
        posts = get_posted_content_from_notion(mock_notion_client)
        assert len(posts) == 0
        mock_print.assert_called_with("Error querying Notion for posted content: Notion error")

# Test get_performance_metrics (placeholder function)
def test_get_performance_metrics():
    metrics = get_performance_metrics("some_id", "Facebook")
    assert "likes" in metrics
    assert "comments" in metrics
    assert "reach" in metrics

# Test update_notion_with_metrics
def test_update_notion_with_metrics_success(mock_notion_client):
    metrics = {"likes": 100, "comments": 10, "reach": 1000}
    update_notion_with_metrics(mock_notion_client, "page123", metrics)
    mock_notion_client.pages.update.assert_called_once_with(
        page_id="page123",
        properties={
            "Likes": {"number": 100},
            "Comments": {"number": 10},
            "Reach": {"number": 1000}
        }
    )

def test_update_notion_with_metrics_exception(mock_notion_client):
    mock_notion_client.pages.update.side_effect = Exception("Notion update error")
    metrics = {"likes": 100, "comments": 10, "reach": 1000}
    with patch('builtins.print') as mock_print:
        update_notion_with_metrics(mock_notion_client, "page123", metrics)
        mock_print.assert_called_with("Error updating Notion page page123: Notion update error")

# Test main function
def test_main_success(mock_notion_client):
    mock_notion_client.databases.query.return_value = {
        "results": [
            {"id": "page1", "properties": {"Platform": {"select": {"name": "Facebook"}}, "Post ID": {"rich_text": [{"text": {"content": "fb_post_1"}}]}}}
        ]
    }
    with patch('src.track_performance.get_performance_metrics') as mock_get_metrics,
         patch('src.track_performance.update_notion_with_metrics') as mock_update_notion,
         patch('builtins.print') as mock_print:
        mock_get_metrics.return_value = {"likes": 50, "comments": 5, "reach": 500}
        main()
        mock_get_metrics.assert_called_once_with("fb_post_1", "Facebook")
        mock_update_notion.assert_called_once_with(mock_notion_client.return_value, "page1", {"likes": 50, "comments": 5, "reach": 500})
        mock_print.assert_any_call("Finished tracking performance.")

def test_main_no_posts_to_track(mock_notion_client):
    mock_notion_client.databases.query.return_value = {"results": []}
    with patch('src.track_performance.get_performance_metrics') as mock_get_metrics,
         patch('src.track_performance.update_notion_with_metrics') as mock_update_notion,
         patch('builtins.print') as mock_print:
        main()
        mock_get_metrics.assert_not_called()
        mock_update_notion.assert_not_called()
        mock_print.assert_any_call("No new posts to track.")

def test_main_missing_platform_or_post_id(mock_notion_client):
    mock_notion_client.databases.query.return_value = {
        "results": [
            {"id": "page1", "properties": {"Platform": {"select": {"name": "Facebook"}}}}, # Missing Post ID
            {"id": "page2", "properties": {"Post ID": {"rich_text": [{"text": {"content": "ig_post_1"}}]}}} # Missing Platform
        ]
    }
    with patch('src.track_performance.get_performance_metrics') as mock_get_metrics,
         patch('src.track_performance.update_notion_with_metrics') as mock_update_notion,
         patch('builtins.print') as mock_print:
        main()
        mock_get_metrics.assert_not_called()
        mock_update_notion.assert_not_called()
        mock_print.assert_any_call("Skipping page page1 due to missing Platform or Post ID.")
        mock_print.assert_any_call("Skipping page page2 due to missing Platform or Post ID.")

def test_main_missing_env_vars():
    with patch.dict(os.environ, {"NOTION_TOKEN": ""}),\
         pytest.raises(ValueError, match="NOTION_TOKEN and DATABASE_ID must be set in the .env file."): 
        main()
