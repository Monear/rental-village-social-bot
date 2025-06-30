import os
import pytest
import json
from unittest.mock import patch, MagicMock
from utils import gemini_helpers

# Patch environment variable for API key
def setup_module(module):
    os.environ["GEMINI_API_KEY"] = "fake-key"

def teardown_module(module):
    if "GEMINI_API_KEY" in os.environ:
        del os.environ["GEMINI_API_KEY"]

def test_generate_ideas_with_gemini_success():
    fake_guidelines = "Be creative."
    fake_num_ideas = 1
    fake_user_input = "Lawn care tips."
    fake_json = [
        {
            "pillar": "Tool Spotlight",
            "title": "Mini-Excavator: Small But Mighty",
            "body": "Check out this 15-second video...",
            "keywords": "excavator, construction"
        }
    ]
    fake_response = MagicMock()
    fake_response.candidates = [
        MagicMock(content=MagicMock(parts=[MagicMock(text=json.dumps(fake_json))]))
    ]
    with patch("google.genai.Client") as mock_client:
        instance = mock_client.return_value
        instance.models.generate_content.return_value = fake_response
        result = gemini_helpers.generate_ideas_with_gemini(fake_guidelines, fake_num_ideas, fake_user_input)
        assert isinstance(result, list)
        assert result[0]["pillar"] == "Tool Spotlight"


def test_generate_ideas_with_gemini_missing_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with patch("google.genai.Client"):
        with pytest.raises(ValueError):
            gemini_helpers.generate_ideas_with_gemini("guidelines", 1)


def test_generate_ideas_with_gemini_api_error():
    with patch("google.genai.Client") as mock_client:
        instance = mock_client.return_value
        instance.models.generate_content.side_effect = Exception("API error")
        result = gemini_helpers.generate_ideas_with_gemini("guidelines", 1)
        assert result == []


def test_generate_image_with_gemini_success(tmp_path):
    fake_prompt = "A beautiful lawn."
    fake_output = tmp_path / "test.png"
    fake_image_data = b"fakeimagedata"
    fake_part = MagicMock()
    fake_part.inline_data = MagicMock(data=fake_image_data)
    fake_response = MagicMock()
    fake_response.candidates = [MagicMock(content=MagicMock(parts=[fake_part]))]
    with patch("google.genai.Client") as mock_client, \
         patch("google.genai.types.GenerateContentConfig"), \
         patch("PIL.Image.open") as mock_open:
        instance = mock_client.return_value
        instance.models.generate_content.return_value = fake_response
        mock_img = MagicMock()
        mock_open.return_value = mock_img
        result = gemini_helpers.generate_image_with_gemini(fake_prompt, str(fake_output))
        mock_img.save.assert_called_once_with(str(fake_output))
        assert result == str(fake_output)


def test_generate_image_with_gemini_no_image():
    fake_prompt = "No image."
    fake_part = MagicMock()
    fake_part.inline_data = None
    fake_response = MagicMock()
    fake_response.candidates = [MagicMock(content=MagicMock(parts=[fake_part]))]
    with patch("google.genai.Client") as mock_client, \
         patch("google.genai.types.GenerateContentConfig"), \
         patch("PIL.Image.open"):
        instance = mock_client.return_value
        instance.models.generate_content.return_value = fake_response
        result = gemini_helpers.generate_image_with_gemini(fake_prompt, "output.png")
        assert result is None


def test_generate_image_with_gemini_error():
    with patch("google.genai.Client") as mock_client, \
         patch("google.genai.types.GenerateContentConfig"), \
         patch("PIL.Image.open"):
        instance = mock_client.return_value
        instance.models.generate_content.side_effect = Exception("API error")
        result = gemini_helpers.generate_image_with_gemini("prompt", "output.png")
        assert result is None
