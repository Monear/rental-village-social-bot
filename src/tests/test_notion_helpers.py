import os
import pytest
from unittest.mock import patch, MagicMock, mock_open
from utils import notion_helpers

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
    # Patch image generation and upload
    with patch("utils.notion_helpers.generate_image_with_gemini", return_value="img.png"), \
         patch("utils.notion_helpers.upload_image_to_notion", return_value=True):
        notion_helpers.add_idea_to_notion(notion, fake_idea, notion_helpers.generate_image_with_gemini)
        notion.pages.create.assert_called_once()

def test_add_idea_to_notion_image_fail():
    fake_idea = {
        "title": "Test Title",
        "pillar": "Test Pillar",
        "body": "Test Body"
    }
    fake_page = {"id": "pageid"}
    notion = MagicMock()
    notion.pages.create.return_value = fake_page
    with patch("utils.notion_helpers.generate_image_with_gemini", return_value=None):
        notion_helpers.add_idea_to_notion(notion, fake_idea, notion_helpers.generate_image_with_gemini)
        notion.pages.create.assert_called_once()

def test_add_idea_to_notion_exception():
    fake_idea = {
        "title": "Test Title",
        "pillar": "Test Pillar",
        "body": "Test Body"
    }
    notion = MagicMock()
    notion.pages.create.side_effect = Exception("fail")
    notion_helpers.add_idea_to_notion(notion, fake_idea, notion_helpers.generate_image_with_gemini)
