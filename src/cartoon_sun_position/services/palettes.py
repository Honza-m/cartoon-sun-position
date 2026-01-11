import datetime as dt
from typing import TypeVar

from cartoon_sun_position.constants import (
    DAYTIME_COLOUR,
    LOW_SUN_COLOURS,
    LOW_SUN_TIME,
    NIGHT_COLOUR,
    TWILIGHT_COLOURS,
)
from cartoon_sun_position.schemas import Config, Palette
from cartoon_sun_position.utils import get_time_as_pct

T = TypeVar("T")


def get_item_by_time(
    items: list[T],
    current_time: dt.time,
    start_time: dt.time,
    end_time: dt.time,
    reverse=False,
) -> T:
    if reverse:
        items = list(reversed(items))

    pct = get_time_as_pct(current_time, start_time, end_time)
    index = int(pct * (len(items) - 1))
    return items[index]


def add_time(t1: dt.time, hours: int):
    if t1.hour + hours > 23:
        return dt.time.max

    return dt.time(hour=t1.hour + hours, minute=t1.minute, second=t1.second)


def sub_time(t1: dt.time, hours: int):
    if t1.hour - hours < 0:
        return dt.time.min

    return dt.time(hour=t1.hour - hours, minute=t1.minute, second=t1.second)


def get_current_palette(ct: dt.time, cfg: Config) -> Palette:
    """Given current time and config, return current pallete to use for rendering"""
    rising_plus = add_time(cfg["rising"], LOW_SUN_TIME)
    setting_minus = sub_time(cfg["setting"], LOW_SUN_TIME)

    if ct < cfg["dawn"] or ct >= cfg["dusk"]:
        return NIGHT_COLOUR
    elif ct >= cfg["dawn"] and ct < cfg["rising"]:
        return get_item_by_time(TWILIGHT_COLOURS, ct, cfg["dawn"], cfg["rising"])
    elif ct >= cfg["setting"] and ct < cfg["dusk"]:
        return get_item_by_time(TWILIGHT_COLOURS, ct, cfg["setting"], cfg["dusk"], True)
    elif ct >= cfg["rising"] and ct < rising_plus:
        return get_item_by_time(LOW_SUN_COLOURS, ct, cfg["rising"], rising_plus)
    elif ct >= setting_minus and ct < cfg["setting"]:
        return get_item_by_time(
            LOW_SUN_COLOURS, ct, setting_minus, cfg["setting"], True
        )
    else:
        return DAYTIME_COLOUR
