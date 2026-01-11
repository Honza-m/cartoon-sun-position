from PIL import Image, ImageColor, ImageDraw, ImageFont

from constants import BACK_IMG, FONT_HOURS, FRONT_IMG, MID_IMG, SUN_COLOR, SUN_RADIUS
from schemas import Config, Coor, Palette
from utils import adjust, colorize_mask, vertical_gradient_rgb


def get_base_image(palette: Palette, sun_position: Coor | None) -> Image.Image:
    base_size = Image.open(BACK_IMG).size
    (dark, mid, light) = palette
    light_rgb = ImageColor.getrgb(light)

    # Sky gradient
    sky_top = adjust(light_rgb, 1.22)
    sky_bottom = adjust(light_rgb, 1.05)

    canvas = vertical_gradient_rgb(base_size, sky_top, sky_bottom)

    # Sun
    if sun_position:
        sun_rgb = ImageColor.getrgb(SUN_COLOR)
        sun_x, sun_y = sun_position
        draw = ImageDraw.Draw(canvas)
        draw.ellipse(
            [
                (sun_x - SUN_RADIUS, sun_y - SUN_RADIUS),
                (sun_x + SUN_RADIUS, sun_y + SUN_RADIUS),
            ],
            fill=sun_rgb,
        )

    # Back mountain
    back_img, back_alpha = colorize_mask(BACK_IMG, light)
    canvas.paste(back_img, mask=back_alpha)

    # Mid mountain
    mid_img, mid_alpha = colorize_mask(MID_IMG, mid)
    canvas.paste(mid_img, mask=mid_alpha)

    # Front mountain
    front_img, front_alpha = colorize_mask(FRONT_IMG, dark)
    canvas.paste(front_img, mask=front_alpha)

    return canvas


def add_sunrise_sunset_info(canvas: Image.Image, cfg: Config) -> Image.Image:
    canvas_x, canvas_y = canvas.size
    padding = 50
    coors = (
        canvas_x - padding,
        canvas_y - padding,
    )

    sunrise = cfg["rising"].strftime("%H:%M")
    sunset = cfg["setting"].strftime("%H:%M")
    text = f"{sunrise} | {sunset}"

    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype(FONT_HOURS, size=64)
    draw.text(coors, text, fill=(255, 255, 255), font=font, anchor="rb")
    return canvas
