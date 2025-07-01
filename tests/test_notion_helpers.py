import os
import pytest
from unittest.mock import patch, MagicMock, mock_open
from src.utils import notion_helpers

# Set GEMINI_API_KEY for all tests
os.environ["GEMINI_API_KEY"] = "fake-key"

# Patch environment variables for Notion
NOTION_API_KEY = "fake-notion-key"
NOTION_DATABASE_ID = "fake-db-id"
os.environ["NOTION_API_KEY"] = NOTION_API_KEY
os.environ["NOTION_DATABASE_ID"] = NOTION_DATABASE_ID

def test_upload_image_to_notion_success():
    page_id = "page123"
    image_path = "fake_image.png"
    # Mock all requests and file open
    with patch("requests.post") as mock_post, \
         patch("requests.get") as mock_get, \
         patch("requests.patch") as mock_patch, \
         patch("builtins.open", mock_open(read_data=b"fake")):
        # Step 1: initiate upload
        mock_post.side_effect = [
            MagicMock(status_code=200, json=lambda: {"id": "uploadid"}),  # initiate
            MagicMock(status_code=200, json=lambda: {"status": "ok"})      # upload
        ]
        # Step 2: get page
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {"properties": {"Creative": {"files": []}}})
        # Step 3: patch page
        mock_patch.return_value = MagicMock(status_code=200)
        result = notion_helpers.upload_image_to_notion(page_id, image_path)
        assert result is True

def test_upload_image_to_notion_http_error():
    with patch("requests.post") as mock_post:
        mock_post.side_effect = Exception("HTTP Error")
        result = notion_helpers.upload_image_to_notion("pageid", "img.png")
        assert result is False

def test_upload_image_to_notion_general_error():
    with patch("requests.post", side_effect=Exception("fail")):
        result = notion_helpers.upload_image_to_notion("pageid", "img.png")
        assert result is False

def test_add_idea_to_notion_success():
    fake_idea = {
        "title": "Test Title",
        "pillar": "Test Pillar",
        "body": "Test Body"
    }
    fake_page = {"id": "pageid"}
    notion = MagicMock()
    notion.pages.create.return_value = fake_page
    # Fix: generate_image_with_gemini returns a list of paths
    mock_generate_image = MagicMock(return_value=["/tmp/test_image_v1.png", "/tmp/test_image_v2.png", "/tmp/test_image_v3.png"])
    mock_upload_image = MagicMock(return_value=True)
    
    with patch.object(notion_helpers, "upload_image_to_notion", mock_upload_image):
        notion_helpers.add_idea_to_notion(notion, fake_idea, mock_generate_image, num_images=3) # Pass num_images
        notion.pages.create.assert_called_once()
        mock_generate_image.assert_called_once()
        # Fix: Expect 3 calls to upload_image_to_notion
        assert mock_upload_image.call_count == 3
        mock_upload_image.assert_any_call("pageid", "/tmp/test_image_v1.png")
        mock_upload_image.assert_any_call("pageid", "/tmp/test_image_v2.png")
        mock_upload_image.assert_any_call("pageid", "/tmp/test_image_v3.png")

def test_add_idea_to_notion_image_fail():
    fake_idea = {
        "title": "Test Title",
        "pillar": "Test Pillar",
        "body": "Test Body"
    }
    fake_page = {"id": "pageid"}
    notion = MagicMock()
    notion.pages.create.return_value = fake_page
    mock_generate_image = MagicMock(return_value=None)
    with patch.object(notion_helpers, "upload_image_to_notion", MagicMock()):
        notion_helpers.add_idea_to_notion(notion, fake_idea, mock_generate_image)
        notion.pages.create.assert_called_once()
        mock_generate_image.assert_called_once()

def test_add_idea_to_notion_exception():
    fake_idea = {
        "title": "Test Title",
        "pillar": "Test Pillar",
        "body": "Test Body"
    }
    notion = MagicMock()
    notion.pages.create.side_effect = Exception("fail")
    mock_generate_image = MagicMock()
    with patch.object(notion_helpers, "upload_image_to_notion", MagicMock()):
        notion_helpers.add_idea_to_notion(notion, fake_idea, mock_generate_image)