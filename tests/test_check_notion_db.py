import os
import json
import pytest
from unittest.mock import patch, MagicMock
import importlib
from src.utils import check_notion_db

def reload_check_notion_db():
    importlib.reload(check_notion_db)

@pytest.fixture(autouse=True)
def mock_env_vars():
    with patch.dict(os.environ, {
        "NOTION_API_KEY": "fake_notion_key",
        "NOTION_DATABASE_ID": "fake_notion_db_id",
    }):
        reload_check_notion_db()
        yield

# Mock Notion client
@pytest.fixture
def mock_notion_client():
    with patch('notion_client.Client') as mock_client:
        mock_notion = MagicMock()
        mock_client.return_value = mock_notion
        yield mock_notion

@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("NOTION_API_KEY") or not os.getenv("NOTION_DATABASE_ID"), reason="No Notion API key or DB ID set for integration test.")
def test_main_success_real():
    # This test will make a real API call if NOTION_API_KEY and NOTION_DATABASE_ID are set
    from src.utils import check_notion_db
    check_notion_db.main()
    # If no exception, the test passes (output is printed)

def test_main_missing_env_vars():
    with patch.dict(os.environ, {"NOTION_API_KEY": "", "NOTION_DATABASE_ID": ""}):
        from src.utils import check_notion_db
        import importlib
        importlib.reload(check_notion_db)
        with pytest.raises(ValueError, match="NOTION_API_KEY and NOTION_DATABASE_ID must be set in the .env file."):
            check_notion_db.main()

def test_main_notion_api_error(mock_notion_client):
    mock_notion_client.databases.retrieve.side_effect = Exception("API Error")
    with patch('builtins.print') as mock_print:
        from src.utils import check_notion_db
        check_notion_db.main()
        # Accept any print call containing 'An error occurred:'
        found = any('An error occurred:' in str(call) for call in mock_print.call_args_list)
        assert found, f"Expected a print call containing 'An error occurred:', got: {mock_print.call_args_list}"
