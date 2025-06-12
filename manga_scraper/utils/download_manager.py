import os

def download_and_save_image(response, img_urls, index, folder, file_ext):
    """Download and save the image to the specified folder."""
    # Check for a failed image download (non-image or error response)
    if response.status != 200:
        print(f"❌ Error downloading image, skipping chapter.")
        return False

    ext = os.path.splitext(img_urls[index])[1].split('?')[0].lower() or file_ext
    filename = f"{index + 1:03d}{ext}"
    path = os.path.join(folder, filename)

    try:
        with open(path, 'wb') as f:
            f.write(response.body)
        return True
    except Exception as e:
        print(f"❌ Error saving image {filename}: {e}")
        return False
