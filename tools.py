# tools.py

# Import the 'os' library, which allows us to interact with the
# operating system's file system.
import os

# --- Configuration ---
# Define the name of the directory where our AI can safely work.
# This prevents it from accessing files outside of this folder.
WORKING_DIRECTORY = "workspace"

# --- Initialization ---
def initialize_workspace():
    """
    Ensures the workspace directory exists.
    """
    os.makedirs(WORKING_DIRECTORY, exist_ok=True)

# --- Tool Definitions ---

def read_file(filename: str) -> str:
    """
    Reads the content of a specified file from the workspace.

    Args:
        filename (str): The name of the file to read.

    Returns:
        str: The content of the file, or an error message if it fails.
    """
    print(f"--- [TOOL ACTION] Reading file: {filename} ---")
    try:
        # Create a secure file path by joining the workspace directory and the filename.
        # This prevents "path traversal" attacks where the AI might try to access
        # files outside its designated folder (e.g., by using '../../').
        secure_path = os.path.join(WORKING_DIRECTORY, os.path.basename(filename))
        
        # Open the file in read mode ('r') and return its contents.
        with open(secure_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File '{filename}' not found."
    except Exception as e:
        return f"Error reading file '{filename}': {e}"

def write_file(filename: str, content: str) -> str:
    """
    Writes content to a specified file in the workspace.
    This will create the file if it doesn't exist, or overwrite it if it does.

    Args:
        filename (str): The name of the file to write to.
        content (str): The content to write into the file.

    Returns:
        str: A success message, or an error message if it fails.
    """
    print(f"--- [TOOL ACTION] Writing to file: {filename} ---")
    try:
        # Create a secure file path just like in the read_file function.
        secure_path = os.path.join(WORKING_DIRECTORY, os.path.basename(filename))
        
        # Open the file in write mode ('w'). This will create or overwrite the file.
        with open(secure_path, 'w') as f:
            f.write(content)
        # Return a confirmation message.
        return f"Success: Content written to '{filename}'."
    except Exception as e:
        return f"Error writing to file '{filename}': {e}"

def list_files() -> str:
    """
    Lists all files and directories in the workspace.

    Returns:
        str: A string containing the list of files, or an error message.
    """
    print("--- [TOOL ACTION] Listing files in workspace ---")
    try:
        # Get a list of all items in the working directory.
        items = os.listdir(WORKING_DIRECTORY)
        # If the directory is empty, return a specific message.
        if not items:
            return "The workspace directory is empty."
        # Otherwise, join the list of items into a single string,
        # with each item on a new line for readability.
        return "Files in workspace:\n- " + "\n- ".join(items)
    except Exception as e:
        return f"Error listing files: {e}"

# --- Initial call to set up the workspace on script start ---
initialize_workspace()