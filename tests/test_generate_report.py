import os
import pytest
from unittest.mock import patch, MagicMock, mock_open
from datetime import date
from src.generate_report import main, get_this_months_posted_content, create_markdown_report, save_report_to_file

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

# Test get_this_months_posted_content
def test_get_this_months_posted_content_success(mock_notion_client):
    mock_notion_client.databases.query.return_value = {
        "results": [
            {"properties": {"Name": {"title": [{"text": {"content": "Post 1"}}]}, "Likes": {"number": 10}, "Comments": {"number": 2}, "Reach": {"number": 100}}},
            {"properties": {"Name": {"title": [{"text": {"content": "Post 2"}}]}, "Likes": {"number": 20}, "Comments": {"number": 5}, "Reach": {"number": 200}}}
        ]
    }
    posts = get_this_months_posted_content(mock_notion_client)
    assert len(posts) == 2
    assert posts[0]['properties']['Name']['title'][0]['text']['content'] == "Post 1"

def test_get_this_months_posted_content_no_posts(mock_notion_client):
    mock_notion_client.databases.query.return_value = {"results": []}
    posts = get_this_months_posted_content(mock_notion_client)
    assert len(posts) == 0

def test_get_this_months_posted_content_exception(mock_notion_client):
    mock_notion_client.databases.query.side_effect = Exception("Notion error")
    with patch('builtins.print') as mock_print:
        posts = get_this_months_posted_content(mock_notion_client)
        assert len(posts) == 0
        mock_print.assert_called_with("Error querying Notion for monthly report data: Notion error")

# Test create_markdown_report
def test_create_markdown_report_with_posts():
    posts = [
        {"properties": {"Name": {"title": [{"text": {"content": "Post A"}}]}, "Likes": {"number": 10}, "Comments": {"number": 2}, "Reach": {"number": 100}}},
        {"properties": {"Name": {"title": [{"text": {"content": "Post B"}}]}, "Likes": {"number": 20}, "Comments": {"number": 5}, "Reach": {"number": 200}}},
        {"properties": {"Name": {"title": [{"text": {"content": "Post C"}}]}, "Likes": {"number": 5}, "Comments": {"number": 1}, "Reach": {"number": 50}}}
    ]
    report = create_markdown_report(posts)
    assert "# Social Media Performance Report" in report
    assert "Total Posts: 3" in report
    assert "Total Likes: 35" in report
    assert "Total Comments: 8" in report
    assert "Total Reach: 350" in report
    assert "### 1. Post B" in report # Top post by likes

def test_create_markdown_report_no_posts():
    report = create_markdown_report([])
    assert "No posts with performance data found for this month." in report

# Test save_report_to_file
def test_save_report_to_file_success():
    mock_content = "# Test Report"
    mock_file_path = os.path.join("strategy_documents", f"monthly_report_{date.today().strftime('%Y-%m')}.md")
    with patch('builtins.open', mock_open()) as mocked_file_open:
         patch('builtins.print') as mock_print:
        save_report_to_file(mock_content)
        mocked_file_open.assert_called_once_with(mock_file_path, 'w')
        mocked_file_open().write.assert_called_once_with(mock_content)
        mock_print.assert_called_with(f"Successfully saved report to {mock_file_path}")

def test_save_report_to_file_exception():
    mock_content = "# Test Report"
    with patch('builtins.open', side_effect=Exception("File write error")),
         patch('builtins.print') as mock_print:
        save_report_to_file(mock_content)
        mock_print.assert_called_with("Error saving report file: File write error")

# Test main function
def test_main_success(mock_notion_client):
    mock_notion_client.databases.query.return_value = {
        "results": [
            {"properties": {"Name": {"title": [{"text": {"content": "Post 1"}}]}, "Likes": {"number": 10}, "Comments": {"number": 2}, "Reach": {"number": 100}}}
        ]
    }
    with patch('src.generate_report.save_report_to_file') as mock_save_report,
         patch('builtins.print') as mock_print:
        main()
        mock_save_report.assert_called_once()
        mock_print.assert_any_call("Generating monthly performance report...")
        mock_print.assert_any_call("Report generation complete.")

def test_main_missing_env_vars():
    with patch.dict(os.environ, {"NOTION_TOKEN": ""}),\
         pytest.raises(ValueError, match="NOTION_TOKEN and DATABASE_ID must be set in the .env file."): 
        main()
