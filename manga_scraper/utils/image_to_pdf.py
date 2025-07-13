import os
import img2pdf
from PIL import Image

def convert_folders_to_pdfs(directory: str):
    """
    Convert all image folders under the given directory into PDF files.
    Each subfolder becomes one PDF named as Volume_01.pdf, Volume_02.pdf, etc.

    Args:
        directory (str): Path to the main directory containing subfolders with images.
    """
    if not os.path.isdir(directory):
        print(f"Error: Directory '{directory}' does not exist.")
        return

    # Get all subdirectories under the given directory, sorted by name
    volumes = sorted([
        d for d in os.listdir(directory)
        if os.path.isdir(os.path.join(directory, d))
    ])

    for index, volume in enumerate(volumes, start=1):
        volume_dir = os.path.join(directory, volume)

        # Collect all image files in sorted order
        image_files = [
            os.path.join(volume_dir, file)
            for file in sorted(os.listdir(volume_dir))
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))
        ]

        if not image_files:
            print(f"Warning: No images found in {volume}, skipping...")
            continue

        # Format output PDF filename as Volume_01.pdf, Volume_02.pdf, etc.
        output_pdf = os.path.join(directory, f"Volume_{index:02d}.pdf")

        try:
            # Open output file in binary write mode
            with open(output_pdf, "wb") as f:
                processed_imgs = []
                for img_path in image_files:
                    with Image.open(img_path) as img:
                        if img.mode in ("RGBA", "P"):
                            img = img.convert("RGB")
                            img.save(img_path)  # Overwrite the original image
                    processed_imgs.append(img_path)

                f.write(img2pdf.convert(processed_imgs))

            print(f"Successfully created: {output_pdf}")

        except Exception as e:
            print(f"Failed to process {volume}: {str(e)}")

