import datetime as dt

from cartoon_sun_position.adapters.hash_cache import _compute_image_hash, read_hash
from cartoon_sun_position.config import get_config
from cartoon_sun_position.services.palettes import get_current_palette
from cartoon_sun_position.services.sun import get_sun_position


def image_will_change() -> bool:
    cfg = get_config()
    ct = dt.datetime.now().time()
    palette = get_current_palette(ct, cfg)
    sun = get_sun_position(ct, cfg)
    digest = _compute_image_hash(cfg, palette, sun)
    stored = read_hash()
    return stored is None or stored != digest
