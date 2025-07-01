import os
import json
import pytest
from unittest.mock import patch, MagicMock, mock_open
from src.suggest_content import main
from src.utils.general import read_file_content

# Mock environment variables for testing
@pytest.fixture(autouse=True)
def mock_env_vars():
    with patch.dict(os.environ, {
        "NOTION_API_KEY": "fake_notion_key",
        "NOTION_DATABASE_ID": "fake_notion_db_id",
        "GEMINI_API_KEY": "fake_gemini_key",
    }):
        yield

# Mock read_file_content for prompt files
@pytest.fixture
def mock_read_file_content():
    with patch('src.utils.general.read_file_content') as mock_read:
        mock_read.side_effect = lambda x: {
            'src/prompts/content_generation_prompt.md': 'Content Guidelines',
            'src/prompts/social_media_best_practices.md': 'Social Media Best Practices',
            'src/prompts/image_generation_instructions.md': 'Image Instructions'
        }.get(x, None)
        yield mock_read

# Mock Notion API interactions
@pytest.fixture
def mock_notion_client():
    with patch('notion_client.Client') as mock_client:
        mock_notion = MagicMock()
        mock_client.return_value = mock_notion
        mock_notion.databases.query.return_value = {"results": []} # No existing ideas by default
        mock_notion.pages.create.return_value = {"id": "new_page_id"}
        yield mock_notion

# Mock Gemini API interactions
@pytest.fixture
def mock_gemini_helpers():
    with patch('src.utils.gemini_helpers.generate_ideas_with_gemini') as mock_ideas:
        with patch('src.utils.gemini_helpers.generate_image_with_gemini') as mock_images:
            mock_ideas.return_value = [
            {
                "pillar": "Tool Spotlight",
                "title": "Test Idea",
                "body": "This is a test body.",
                "keywords": "test, image"
            }
        ]
        mock_images.return_value = ["/tmp/test_image_v1.png"]
        yield mock_ideas, mock_images

# Mock Notion helpers for add_idea_to_notion and get_existing_notion_ideas
@pytest.fixture
def mock_notion_helpers():
    with (
        patch('src.utils.notion_helpers.add_idea_to_notion') as mock_add_idea,
        patch('src.utils.notion_helpers.get_existing_notion_ideas') as mock_get_ideas
    ):
        mock_add_idea.return_value = None
        mock_get_ideas.return_value = [] # No existing ideas by default
        yield mock_add_idea, mock_get_ideas

# Mock machine_context.json loading
@pytest.fixture
def mock_machine_context():
    with patch('builtins.open', mock_open(read_data=json.dumps({
        "business_info": {"name": "Test Business"},
        "available_machines": [{"name": "Test Machine"}]
    }))) as mock_file:
        yield mock_file


def test_main_success(
    mock_env_vars,
    mock_read_file_content,
    mock_notion_client,
    mock_gemini_helpers,
    mock_notion_helpers,
    mock_machine_context,
):
    with patch.dict(os.environ, {"NOTION_API_KEY": "fake_notion_key", "NOTION_DATABASE_ID": "fake_notion_db_id", "GEMINI_API_KEY": "fake_gemini_key"}):
        from src import suggest_content as suggest_content_module
        import importlib
        importlib.reload(suggest_content_module)
        script_dir = os.path.dirname(suggest_content_module.__file__)
        guidelines_path = os.path.join(script_dir, 'prompts', 'content_generation_prompt.md')
        best_practices_path = os.path.join(script_dir, 'prompts', 'social_media_best_practices.md')
        image_instructions_path = os.path.join(script_dir, 'prompts', 'image_generation_instructions.md')
        mock_read_file_content.side_effect = lambda x: {
            guidelines_path: 'Content Guidelines',
            best_practices_path: 'Social Media Best Practices',
            image_instructions_path: 'Image Instructions'
        }.get(x, 'Content Guidelines')
        with patch('builtins.print') as mock_print, patch('sys.argv', ["suggest_content.py", "--num-ideas", "1"]):
            suggest_content_module.main()
            mock_read_file_content.assert_any_call(guidelines_path)
            mock_read_file_content.assert_any_call(best_practices_path)
            # Just check it was called, not with exact args
            assert mock_notion_helpers[1].called
            assert mock_gemini_helpers[0].called
            assert mock_notion_helpers[0].called
            mock_print.assert_any_call("Fetching existing ideas from Notion...")
            mock_print.assert_any_call("Found 0 existing ideas.")
            mock_print.assert_any_call("\nStarting to add new content ideas to Notion...")
            mock_print.assert_any_call("Finished adding ideas.")

def test_main_no_content_guidelines(
    mock_env_vars,
    mock_read_file_content,
    mock_notion_client,
    mock_gemini_helpers,
    mock_notion_helpers,
    mock_machine_context,
):
    with patch.dict(os.environ, {"NOTION_API_KEY": "fake_notion_key", "NOTION_DATABASE_ID": "fake_notion_db_id", "GEMINI_API_KEY": "fake_gemini_key"}):
        from src import suggest_content as suggest_content_module
        import importlib
        importlib.reload(suggest_content_module)
        script_dir = os.path.dirname(suggest_content_module.__file__)
        guidelines_path = os.path.join(script_dir, 'prompts', 'content_generation_prompt.md')
        best_practices_path = os.path.join(script_dir, 'prompts', 'social_media_best_practices.md')
        image_instructions_path = os.path.join(script_dir, 'prompts', 'image_generation_instructions.md')
        mock_read_file_content.side_effect = lambda x: {
            guidelines_path: None,
            best_practices_path: 'Social Media Best Practices',
            image_instructions_path: 'Image Instructions'
        }.get(x, None)
        with patch('builtins.print') as mock_print, patch('sys.argv', ["suggest_content.py", "--num-ideas", "1"]):
            suggest_content_module.main()
            mock_print.assert_not_called()

def test_main_no_ideas_generated(
    mock_env_vars,
    mock_read_file_content,
    mock_notion_client,
    mock_gemini_helpers,
    mock_notion_helpers,
    mock_machine_context,
):
    with patch.dict(os.environ, {"NOTION_API_KEY": "fake_notion_key", "NOTION_DATABASE_ID": "fake_notion_db_id", "GEMINI_API_KEY": "fake_gemini_key"}):
        from src import suggest_content as suggest_content_module
        import importlib
        importlib.reload(suggest_content_module)
        script_dir = os.path.dirname(suggest_content_module.__file__)
        guidelines_path = os.path.join(script_dir, 'prompts', 'content_generation_prompt.md')
        best_practices_path = os.path.join(script_dir, 'prompts', 'social_media_best_practices.md')
        image_instructions_path = os.path.join(script_dir, 'prompts', 'image_generation_instructions.md')
        mock_read_file_content.side_effect = lambda x: {
            guidelines_path: 'Content Guidelines',
            best_practices_path: 'Social Media Best Practices',
            image_instructions_path: 'Image Instructions'
        }.get(x, 'Content Guidelines')
        mock_gemini_helpers[0].return_value = []
        with patch('builtins.print') as mock_print, patch('sys.argv', ["suggest_content.py", "--num-ideas", "1"]):
            suggest_content_module.main()
            mock_print.assert_any_call("No ideas were generated. Exiting.")

def test_main_missing_env_vars():
    with patch.dict(os.environ, {
        "NOTION_API_KEY": "",
        "NOTION_DATABASE_ID": "fake_notion_db_id",
        "GEMINI_API_KEY": "fake_gemini_key",
    }):
        from src import suggest_content as suggest_content_module
        import importlib
        importlib.reload(suggest_content_module)
        with patch('sys.argv', ["suggest_content.py", "--num-ideas", "1"]):
            with pytest.raises(ValueError, match="Required API keys"):
                suggest_content_module.main()

def test_main_machine_context_missing(
    mock_env_vars,
    mock_read_file_content,
    mock_notion_client,
    mock_gemini_helpers,
    mock_notion_helpers,
):
    with patch.dict(os.environ, {"NOTION_API_KEY": "fake_notion_key", "NOTION_DATABASE_ID": "fake_notion_db_id", "GEMINI_API_KEY": "fake_gemini_key"}):
        from src import suggest_content as suggest_content_module
        import importlib
        importlib.reload(suggest_content_module)
        script_dir = os.path.dirname(suggest_content_module.__file__)
        guidelines_path = os.path.join(script_dir, 'prompts', 'content_generation_prompt.md')
        best_practices_path = os.path.join(script_dir, 'prompts', 'social_media_best_practices.md')
        image_instructions_path = os.path.join(script_dir, 'prompts', 'image_generation_instructions.md')
        mock_read_file_content.side_effect = lambda x: {
            guidelines_path: 'Content Guidelines',
            best_practices_path: 'Social Media Best Practices',
            image_instructions_path: 'Image Instructions'
        }.get(x, 'Content Guidelines')
        with (
            patch('builtins.open', side_effect=FileNotFoundError),
            patch('builtins.print') as mock_print,
            patch('sys.argv', ["suggest_content.py", "--num-ideas", "1"])
        ):
            suggest_content_module.main()
            mcp_path = os.path.join(script_dir, 'data', 'machine_context.json')
            found = any("Warning: Machine context file not found" in str(call) for call in mock_print.call_args_list)
            assert found, f"Expected a print call containing 'Warning: Machine context file not found', got: {mock_print.call_args_list}"

def test_main_mcp_json_decode_error(
    mock_env_vars,
    mock_read_file_content,
    mock_notion_client,
    mock_gemini_helpers,
    mock_notion_helpers,
):
    with patch.dict(os.environ, {"NOTION_API_KEY": "fake_notion_key", "NOTION_DATABASE_ID": "fake_notion_db_id", "GEMINI_API_KEY": "fake_gemini_key"}):
        from src import suggest_content as suggest_content_module
        import importlib
        importlib.reload(suggest_content_module)
        script_dir = os.path.dirname(suggest_content_module.__file__)
        guidelines_path = os.path.join(script_dir, 'prompts', 'content_generation_prompt.md')
        best_practices_path = os.path.join(script_dir, 'prompts', 'social_media_best_practices.md')
        image_instructions_path = os.path.join(script_dir, 'prompts', 'image_generation_instructions.md')
        mock_read_file_content.side_effect = lambda x: {
            guidelines_path: 'Content Guidelines',
            best_practices_path: 'Social Media Best Practices',
            image_instructions_path: 'Image Instructions'
        }.get(x, 'Content Guidelines')
        with (
            patch('builtins.open', mock_open(read_data='invalid json')),
            patch('json.load', side_effect=json.JSONDecodeError("Expecting value", "", 0)),
            patch('builtins.print') as mock_print,
            patch('sys.argv', ["suggest_content.py", "--num-ideas", "1"])
        ):
            suggest_content_module.main()
            mcp_path = os.path.join(script_dir, 'data', 'machine_context.json')
            found = any("Warning: Could not decode JSON from" in str(call) for call in mock_print.call_args_list)
            assert found, f"Expected a print call containing 'Warning: Could not decode JSON from', got: {mock_print.call_args_list}"
