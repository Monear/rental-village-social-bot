import os
import json
import pytest
from unittest.mock import patch, MagicMock
from src.utils.gemini_helpers import generate_ideas_with_gemini, generate_image_with_gemini

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

# Test generate_ideas_with_gemini
def test_generate_ideas_with_gemini_success(mock_gemini_client):
    mock_gemini_client.models.generate_content.return_value = MagicMock(
        candidates=[MagicMock(content=MagicMock(parts=[MagicMock(text='```json\n[{"pillar": "Test", "title": "Idea", "body": "Body", "keywords": "key"}]\n```')]))]
    )
    ideas = generate_ideas_with_gemini("guidelines", 1, "user input", [], {}, "best practices")
    assert len(ideas) == 1
    assert ideas[0]["title"] == "Idea"
    mock_gemini_client.models.generate_content.assert_called_once()

def test_generate_ideas_with_gemini_no_api_key():
    # Fix: Directly patch os.getenv to control GEMINI_API_KEY
    with patch('os.getenv', return_value=None) as mock_getenv:
        mock_getenv.side_effect = lambda key, default=None: None if key == "GEMINI_API_KEY" else os.environ.get(key, default)
        with pytest.raises(ValueError, match="GEMINI_API_KEY must be set"):
            generate_ideas_with_gemini("guidelines", 1)

def test_generate_ideas_with_gemini_api_error(mock_gemini_client):
    mock_gemini_client.models.generate_content.side_effect = Exception("API Error")
    with patch('builtins.print') as mock_print:
        ideas = generate_ideas_with_gemini("guidelines", 1)
        assert len(ideas) == 0
        mock_print.assert_called_with(f"Error generating ideas with Gemini: API Error")

def test_generate_ideas_with_gemini_invalid_json(mock_gemini_client):
    mock_gemini_client.models.generate_content.return_value = MagicMock(
        candidates=[MagicMock(content=MagicMock(parts=[MagicMock(text='invalid json')]))]
    )
    with patch('builtins.print') as mock_print:
        ideas = generate_ideas_with_gemini("guidelines", 1)
        assert len(ideas) == 0
        mock_print.assert_called_with(f"Error generating ideas with Gemini: Expecting value: line 1 column 1 (char 0)")

# Test generate_image_with_gemini
def test_generate_image_with_gemini_success(mock_gemini_client, tmp_path):
    mock_gemini_client.models.generate_content.return_value = MagicMock(
        candidates=[MagicMock(content=MagicMock(parts=[MagicMock(inline_data=MagicMock(data=b'fake_image_data'))]))]
    )
    output_file = tmp_path / "output.png"
    with patch('PIL.Image.open') as mock_image_open:
        with patch('os.makedirs'):
            with patch('builtins.open', MagicMock()): # Mock open for saving image
                mock_image_instance = MagicMock()
        mock_image_open.return_value = mock_image_instance

        # Fix: Pass num_images=1 explicitly to match the test's expectation
        image_paths = generate_image_with_gemini("image prompt", str(output_file), num_images=1)
        assert len(image_paths) == 1
        # Fix: Assert with the correct variation path
        assert str(output_file).replace('.png', '_v1.png') in image_paths
        mock_image_open.assert_called_once()
        # Fix: Assert with the correct variation path
        mock_image_instance.save.assert_called_once_with(str(output_file).replace('.png', '_v1.png'))

def test_generate_image_with_gemini_no_image_generated(mock_gemini_client):
    mock_gemini_client.models.generate_content.return_value = MagicMock(
        candidates=[MagicMock(content=MagicMock(parts=[]))]
    )
    with patch('builtins.print') as mock_print:
        image_paths = generate_image_with_gemini("image prompt", "/tmp/output.png", num_images=1)
        assert image_paths is None
        mock_print.assert_called_with("No image generated for variation 1.")

def test_generate_image_with_gemini_api_error(mock_gemini_client):
    mock_gemini_client.models.generate_content.side_effect = Exception("Image API Error")
    with patch('builtins.print') as mock_print:
        image_paths = generate_image_with_gemini("image prompt", "/tmp/output.png", num_images=1)
        assert image_paths is None
        mock_print.assert_called_with("Error generating image with Gemini: Image API Error")

def test_generate_image_with_gemini_instructions_path(mock_gemini_client):
    mock_gemini_client.models.generate_content.return_value = MagicMock(
        candidates=[MagicMock(content=MagicMock(parts=[MagicMock(inline_data=MagicMock(data=b'fake_image_data'))]))]
    )
    with patch('PIL.Image.open') as mock_image_open,
         patch('os.makedirs'),
         patch('builtins.open', mock_open(read_data='Image Instructions Content')) as mock_file_open:
        mock_image_instance = MagicMock()
        mock_image_open.return_value = mock_image_instance

        image_paths = generate_image_with_gemini("image prompt", "/tmp/output.png", num_images=1, instructions_path="fake/instructions.md")
        mock_file_open.assert_called_once_with("fake/instructions.md", 'r')
        mock_gemini_client.models.generate_content.assert_called_once()
        args, kwargs = mock_gemini_client.models.generate_content.call_args
        # The prompt is now a list of parts, so check the content of the parts
        assert "Image Instructions Content" in args[0][0].contents[0].text
        assert "image prompt" in args[0][0].contents[1].text