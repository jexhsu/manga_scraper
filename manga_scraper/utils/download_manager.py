import os

def download_and_save_image(response, img_urls, index, folder,  use_playwright=False):
    """Download and save the image based on the flag."""
    if use_playwright:
        return download_and_save_image_async(response, img_urls, index, folder)
    else:
        return download_and_save_image_sync(response, img_urls, index, folder)

def download_and_save_image_sync(response, img_urls, index, folder):
    """Synchronously download and save the image."""
    # Check for a failed image download (non-image or error response)
    if response.status != 200:
        print(f"❌ Error downloading image, skipping chapter.")
        return False

    ext = os.path.splitext(img_urls[index])[1].split('?')[0].lower() 
    filename = f"{index + 1:03d}{ext}"
    path = os.path.join(folder, filename)

    try:
        with open(path, 'wb') as f:
            f.write(response.body)
        return True
    except Exception as e:
        print(f"❌ Error saving image {filename}: {e}")
        return False

async def download_and_save_image_async(page, img_url, index, folder):
    """
    Asynchronously download and save an image using Playwright's browser context.
    """
    try:
        img_response = await page.request.get(img_url)
        if img_response.status != 200:
            return False
        
        content = await img_response.body()
        ext = os.path.splitext(img_url)[1].split('?')[0].lower()
        filename = f"{index + 1:03d}{ext}"
        path = os.path.join(folder, filename)

        with open(path, "wb") as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"❌ Error downloading image {img_url}: {e}")
        return False
