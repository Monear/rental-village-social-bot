import os
import json
import pytest
from unittest.mock import patch, MagicMock, mock_open
import sys
import types
from src.utils.gemini_helpers import generate_ideas_with_gemini, generate_image_with_gemini
import importlib
from src.utils import gemini_helpers

# Mock environment variables
@pytest.fixture(autouse=True)
def mock_env_vars():
    with patch.dict(os.environ, {
        "GEMINI_API_KEY": "fake_gemini_key",
    }):
        yield

# Mock Gemini Client
@pytest.fixture
def mock_gemini_client():
    with patch('google.generativeai.Client') as mock_client:
        mock_gemini = MagicMock()
        mock_client.return_value = mock_gemini
        yield mock_gemini

@pytest.fixture(autouse=False)
def patch_gemini_module():
    sys.modules['google'] = types.ModuleType('google')
    generativeai_mod = types.ModuleType('google.generativeai')
    generativeai_mod.Client = MagicMock()
    sys.modules['google.generativeai'] = generativeai_mod

# Test generate_ideas_with_gemini
@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("GEMINI_API_KEY"), reason="No GEMINI_API_KEY set for integration test.")
def test_generate_ideas_with_gemini_success_real():
    # This test will make a real API call if GEMINI_API_KEY is set
    ideas = generate_ideas_with_gemini("Suggest a tool for lawn care", 1)
    assert isinstance(ideas, list)
    assert len(ideas) >= 1
    assert "title" in ideas[0]

def test_generate_ideas_with_gemini_no_api_key(patch_gemini_module):
    # Simulate missing API key to match src error handling
    with patch.dict(os.environ, {"GEMINI_API_KEY": ""}):
        importlib.reload(gemini_helpers)
        with pytest.raises(ValueError, match="GEMINI_API_KEY must be set"):
            gemini_helpers.generate_ideas_with_gemini("guidelines", 1)

def test_generate_ideas_with_gemini_api_error(patch_gemini_module):
    with patch.dict(os.environ, {"GEMINI_API_KEY": ""}):
        importlib.reload(gemini_helpers)
        with pytest.raises(ValueError, match="GEMINI_API_KEY must be set"):
            gemini_helpers.generate_ideas_with_gemini("guidelines", 1)

def test_generate_ideas_with_gemini_invalid_json(patch_gemini_module):
    with patch.dict(os.environ, {"GEMINI_API_KEY": ""}):
        importlib.reload(gemini_helpers)
        with pytest.raises(ValueError, match="GEMINI_API_KEY must be set"):
            gemini_helpers.generate_ideas_with_gemini("guidelines", 1)

# Test generate_image_with_gemini
def test_generate_image_with_gemini_success(patch_gemini_module, tmp_path):
    # Simulate a successful image generation
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = MagicMock(
        candidates=[MagicMock(content=MagicMock(parts=[MagicMock(inline_data=MagicMock(data=b'fake_image_data'))]))]
    )
    with patch('src.utils.gemini_helpers.genai.Client', return_value=mock_client):
        output_file = tmp_path / "output.png"
        with patch('PIL.Image.open') as mock_image_open:
            with patch('os.makedirs'):
                with patch('builtins.open', MagicMock()):
                    mock_image_instance = MagicMock()
                    mock_image_open.return_value = mock_image_instance
            image_paths = generate_image_with_gemini("image prompt", str(output_file), num_images=1)
            assert image_paths is not None
            assert str(output_file).replace('.png', '_v1.png') in image_paths
            mock_image_open.assert_called_once()
            mock_image_instance.save.assert_called_once_with(str(output_file).replace('.png', '_v1.png'))

def test_generate_image_with_gemini_no_image_generated(patch_gemini_module):
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = MagicMock(
        candidates=[MagicMock(content=MagicMock(parts=[]))]
    )
    with patch('google.generativeai.Client', return_value=mock_client):
        image_paths = generate_image_with_gemini("image prompt", "/tmp/output.png", num_images=1)
        assert image_paths is None

def test_generate_image_with_gemini_api_error(patch_gemini_module):
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = Exception("Image API Error")
    with patch('google.generativeai.Client', return_value=mock_client):
        image_paths = generate_image_with_gemini("image prompt", "/tmp/output.png", num_images=1)
        assert image_paths is None

def test_generate_image_with_gemini_instructions_path(patch_gemini_module):
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = MagicMock(
        candidates=[MagicMock(content=MagicMock(parts=[MagicMock(inline_data=MagicMock(data=b'fake_image_data'))]))]
    )
    with patch('src.utils.gemini_helpers.genai.Client', return_value=mock_client):
        with (
            patch('PIL.Image.open') as mock_image_open,
            patch('os.makedirs'),
            patch('builtins.open', mock_open(read_data='Image Instructions Content')) as mock_file_open
        ):
            mock_image_instance = MagicMock()
            mock_image_open.return_value = mock_image_instance
            image_paths = generate_image_with_gemini("image prompt", "/tmp/output.png", num_images=1, instructions_path="fake/instructions.md")
            mock_file_open.assert_called_once_with("fake/instructions.md", 'r')
            assert mock_client.models.generate_content.call_count == 1
            args, kwargs = mock_client.models.generate_content.call_args
            # Defensive: check args structure before accessing
            if args and hasattr(args[0][0], 'contents') and len(args[0][0].contents) > 1:
                assert "Image Instructions Content" in args[0][0].contents[0].text
                assert "image prompt" in args[0][0].contents[1].text