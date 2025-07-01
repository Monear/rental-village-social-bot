import os
import pytest
from unittest.mock import mock_open, patch
from src.utils.general import read_file_content

def test_read_file_content_success():
    mock_data = "This is a test file content."
    with patch("builtins.open", mock_open(read_data=mock_data)) as mock_file:
        content = read_file_content("fake/path/to/file.txt")
        mock_file.assert_called_once_with("fake/path/to/file.txt", 'r')
        assert content == mock_data

def test_read_file_content_file_not_found():
    with patch("builtins.open", side_effect=FileNotFoundError) as mock_file:
        with patch('builtins.print') as mock_print:
            content = read_file_content("nonexistent/file.txt")
        mock_file.assert_called_once_with("nonexistent/file.txt", 'r')
        mock_print.assert_called_once_with("Error: The file nonexistent/file.txt was not found.")
        assert content is None
