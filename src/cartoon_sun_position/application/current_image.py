import datetime as dt

from PIL import Image

from cartoon_sun_position.adapters.output import save_image
from cartoon_sun_position.config import get_config
from cartoon_sun_position.services.image import add_sunrise_sunset_info, get_base_image
from cartoon_sun_position.services.palettes import get_current_palette
from cartoon_sun_position.services.sun import get_sun_position


def generate_image() -> Image.Image:
    print("Getting configuration and current time")
    cfg = get_config()
    ct = dt.datetime.now().time()

    print("Generating color palette and sun position")
    palette = get_current_palette(ct, cfg)
    sun = get_sun_position(ct, cfg)

    print("Creating image")
    image = get_base_image(palette, sun)
    image = add_sunrise_sunset_info(image, cfg)
    return image


def generate_to_file():
    image = generate_image()
    save_image(image)
    print("Image saved successfully")
