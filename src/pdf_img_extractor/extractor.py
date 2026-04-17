from pdf2image import convert_from_path
import os
import datetime
import random
import string


def generate_dir_name(prefix="dir"):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    rand = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{prefix}_{timestamp}_{rand}"


def pdf_to_images(pdf_path, page_number, dpi=200, fmt="png"):
    output_dir = generate_dir_name()
    os.makedirs(output_dir, exist_ok=True)

    images = convert_from_path(
        pdf_path, dpi=dpi, first_page=page_number, last_page=page_number
    )

    image_path = os.path.join(output_dir, f"page_{page_number}.{fmt}")
    images[0].save(image_path, fmt.upper())

    return image_path
