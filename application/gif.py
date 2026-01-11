import datetime as dt

from adapters.output import save_images_as_gif
from config import get_config
from services.image import get_base_image
from services.palettes import get_current_palette
from services.sun import get_sun_position


def create_gif():
    cfg = get_config()
    frames = []
    for h in range(6, 17):
        for m in range(0, 51, 10):
            ct = dt.time(h, m, 0)
            palette = get_current_palette(ct, cfg)
            sun = get_sun_position(ct, cfg)
            image = get_base_image(palette, sun)
            frames.append(image)

    save_images_as_gif(frames)
