import datetime as dt

from PIL import Image, ImageColor


def clamp(x):
    return max(0, min(255, int(x)))


def adjust(rgb, factor):
    return tuple(clamp(c * factor) for c in rgb)


def lerp(a, b, t):
    """Linear interpolation, returns a if t==0, b if t==1, a value in between if 0 < t < 1"""
    return int(a + (b - a) * t)


def mix(c1, c2, t):
    return tuple(lerp(c1[i], c2[i], t) for i in range(3))


def vertical_gradient_rgb(size, top_rgb, bottom_rgb):
    w, h = size
    img = Image.new("RGB", size)
    px = img.load()

    if not px:
        raise ValueError("Couldn't create new image")

    for y in range(h):
        t = y / (h - 1)
        r, g, b = mix(top_rgb, bottom_rgb, t)
        for x in range(w):
            px[x, y] = (r, g, b)

    return img


def colorize_mask(path, color_hex):
    src = Image.open(path).convert("RGBA")
    alpha = src.getchannel("A")

    r, g, b, *_ = ImageColor.getrgb(color_hex)
    colored = Image.new("RGB", src.size, (r, g, b))

    return colored, alpha


def get_time_as_pct(
    current_time: dt.time, start_time: dt.time, end_time: dt.time
) -> float:
    if start_time > end_time:
        raise ValueError("Start time can't be bigger than end time")
    if current_time < start_time or current_time > end_time:
        raise ValueError("Current time needs to be inside start and end time interval")

    def time_to_seconds(t: dt.time) -> int:
        return t.hour * 60 * 60 + t.minute * 60 + t.second

    start_seconds = time_to_seconds(start_time)
    end_seconds = time_to_seconds(end_time)
    current_seconds = time_to_seconds(current_time)

    return (current_seconds - start_seconds) / (end_seconds - start_seconds)
