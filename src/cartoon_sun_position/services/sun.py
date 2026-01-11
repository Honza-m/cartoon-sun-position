import datetime as dt

from cartoon_sun_position.constants import SUN_ARC_HEIGHT, SUNRISE_COOR, SUNSET_COOR
from cartoon_sun_position.schemas import Config, Coor
from cartoon_sun_position.utils import get_time_as_pct, lerp


def get_sun_position(ct: dt.time, cfg: Config) -> Coor | None:
    """
    Returns (x, y) for sun center above mountains, or None at night.
    """
    # Sun position is None at night
    if ct < cfg["rising"] or ct > cfg["setting"]:
        return None

    pct = get_time_as_pct(ct, cfg["rising"], cfg["setting"])

    # X coor
    x = lerp(SUNRISE_COOR[0], SUNSET_COOR[0], pct)

    # Y coor
    baseline_y = lerp(SUNRISE_COOR[1], SUNSET_COOR[1], pct)
    arc = 4 * pct * (1 - pct)  # parabola: 0 → 1 → 0
    y = baseline_y - SUN_ARC_HEIGHT * arc

    return int(x), int(y)
