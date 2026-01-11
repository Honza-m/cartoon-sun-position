import datetime as dt

from cartoon_sun_position.adapters.output import save_images_as_gif
from cartoon_sun_position.config import get_config
from cartoon_sun_position.services.image import get_base_image
from cartoon_sun_position.services.palettes import get_current_palette
from cartoon_sun_position.services.sun import get_sun_position


def generate_gif_to_file():
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
