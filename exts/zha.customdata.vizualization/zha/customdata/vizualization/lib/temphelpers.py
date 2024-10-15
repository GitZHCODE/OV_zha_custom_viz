import os
import tempfile

import uuid
from PIL import Image


def save_temp_image(image, prefix="temp_", suffix=".png"):
    """
    Save a PIL Image object as a temporary file.

    Args:
    image (PIL.Image.Image): The image to save.
    prefix (str): Prefix for the temporary filename.
    suffix (str): Suffix for the temporary filename (file extension).

    Returns:
    str: The path to the saved temporary image file.
    """
    # Create a temporary directory if it doesn't exist
    temp_dir = tempfile.gettempdir()

    # Generate a unique filename
    unique_filename = f"{prefix}{uuid.uuid4()}{suffix}"
    temp_path = os.path.join(temp_dir, unique_filename)

    # Save the image
    image.save(temp_path)

    return temp_path