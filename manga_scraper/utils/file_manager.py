import os
import shutil

def create_download_folder(root_dir, site_name, chapter):
    """Create a folder for the chapter if it doesn't exist."""
    folder = os.path.join(root_dir, site_name, f"chapter-{chapter}")
    os.makedirs(folder, exist_ok=True)
    return folder

def check_existing_downloads(folder, file_ext):
    """Check if there are any existing downloads for the chapter."""
    return len([f for f in os.listdir(folder) if f.endswith(file_ext)])

def remove_folder(folder):
    """Remove the folder if it exists."""
    if os.path.exists(folder):
        shutil.rmtree(folder)
        print(f"🗑️ Removed folder: {folder}\n")
