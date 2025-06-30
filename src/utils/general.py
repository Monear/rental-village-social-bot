# utils/general.py
"""General utility functions."""
def read_file_content(file_path):
    """Reads the content of a specified file."""
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return None
