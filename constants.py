from pathlib import Path

from schemas import Palette

BASE_PATH = Path(__file__).parent
BACK_IMG = BASE_PATH / Path("./static/bitmaps/mountain_back.png")
MID_IMG = BASE_PATH / Path("./static/bitmaps/mountain_mid.png")
FRONT_IMG = BASE_PATH / Path("./static/bitmaps/mountain_front.png")

OUTPUT_DIR = BASE_PATH / Path("./output")

LOW_SUN_TIME = 1
LOW_SUN_COLOURS: list[Palette] = [
    ("#4F3B3A", "#8A5A4E", "#E1A07A"),
    ("#6A5A4A", "#A07C63", "#E2B98A"),
    ("#4A4E4F", "#7A7E74", "#B6B09A"),
    ("#5A6B6B", "#8A9A93", "#C2D0C4"),
]
TWILIGHT_COLOURS: list[Palette] = [
    ("#141E2E", "#24344D", "#3A5075"),
    ("#18253A", "#2A3B57", "#3C5273"),
    ("#2E3440", "#4B5566", "#7A8699"),
]
DAYTIME_COLOUR: Palette = ("#6B7C7A", "#9FAFA8", "#DCE6DD")
NIGHT_COLOUR: Palette = ("#0F1B2D", "#1C2E4A", "#2A4066")

SUN_COLOR = "#F2C94C"

FONT_HOURS = BASE_PATH / Path("./static/fonts/AzeretMono-Regular.ttf")

# TODO: Should be based on image size
SUN_RADIUS = 150
SUNRISE_COOR = (150, 1330)
SUNSET_COOR = (2269, 1230)
SUN_ARC_HEIGHT = 900
