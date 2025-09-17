import os
from PIL import Image

def imagem_para_pdf(image_paths, output_path):
    """
    Converts one or more image files to a single PDF.

    Args:
        image_paths (list): A list of paths to the image files.
        output_path (str): The path to save the output PDF file.

    Returns:
        bool: True if the conversion was successful, False otherwise.
    """
    try:
        images = [Image.open(p).convert("RGB") for p in image_paths]
        if images:
            images[0].save(
                output_path, "PDF", resolution=100.0, save_all=True, append_images=images[1:]
            )
            return True
    except Exception as e:
        print(f"Error converting images to PDF: {e}")
        return False
