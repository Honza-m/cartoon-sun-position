import datetime as dt

from adapters.output import save_image
from config import get_config
from services.image import add_sunrise_sunset_info, get_base_image
from services.palettes import get_current_palette
from services.sun import get_sun_position


def create_current_image():
    print("Getting configuration and current time")
    cfg = get_config()
    ct = dt.datetime.now().time()

    print("Generating color palette and sun position")
    palette = get_current_palette(ct, cfg)
    sun = get_sun_position(ct, cfg)

    print("Creating image")
    image = get_base_image(palette, sun)
    image = add_sunrise_sunset_info(image, cfg)
    save_image(image)
    print("Image saved successfully")
