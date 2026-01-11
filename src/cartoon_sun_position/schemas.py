import datetime as dt
from typing import TypedDict

type Palette = tuple[str, str, str]
type Coor = tuple[int, int]


class Config(TypedDict):
    dawn: dt.time
    dusk: dt.time
    midnight: dt.time | None
    noon: dt.time | None
    rising: dt.time
    setting: dt.time
    valid_for: dt.date
