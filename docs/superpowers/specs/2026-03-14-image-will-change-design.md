# Design: `image_will_change()` — Skip Re-render When Image Is Unchanged

**Date:** 2026-03-14

## Problem

The tool runs on a cron schedule and always calls `generate_image()` + redraws the e-ink display, even when nothing has changed. The primary case: at night (before dawn / after dusk), the image is identical on every run but the display is still redrawn.

## Goal

Expose a cheap `image_will_change() -> bool` function that the calling script can use to skip unnecessary rendering and display updates.

## Usage (calling script)

```python
from cartoon_sun_position import generate_image, image_will_change

if image_will_change():
    image = generate_image()
    resizedimage = image.resize(inky.resolution)
    inky.set_image(resizedimage, saturation=saturation)
    inky.show()
```

## When the Image Is Actually Stable

- **Deep night** (`ct < cfg["dawn"] or ct >= cfg["dusk"]`): palette is `NIGHT_COLOUR` (fixed constant), sun position is `None` → stable hash, `image_will_change()` returns `False` → display skipped. Note: `get_sun_position()` uses `ct > cfg["setting"]` (strict), so at exactly `ct == cfg["setting"]` sun position is still defined — but by that point the palette boundary (`ct >= cfg["dusk"]`) ensures the overall hash is stable regardless.
- **Midnight config rollover:** the config cache invalidates at midnight, fetching new `rising`/`setting` times. The hash will differ from the previous day's and `image_will_change()` correctly returns `True` for the first post-midnight run.
- **Daytime**: sun position is a continuous `(x, y)` function of time (integer-truncated), so the hash changes on most runs. At slow-moving extremes near rise/set, pixel coordinates could be identical across consecutive runs — a minor false negative that skips a negligible redraw. Expected behaviour.
- **Twilight / low-sun windows**: palette transitions through multiple steps, hash changes. Expected.

The primary benefit is eliminating unnecessary display redraws during the night.

## Design

### Hash inputs

The hash covers all inputs that determine the rendered image:

- `palette` — `tuple[str, str, str]` from `get_current_palette()`
- `sun_position` — `tuple[int, int] | None` from `get_sun_position()`
- `cfg["rising"]` and `cfg["setting"]` formatted as `"%H:%M"` — matching how `add_sunrise_sunset_info()` renders them as text on the image

Hash: `SHA-256(str((palette, sun_position, rising_str, setting_str)))`. `str()` is stable because `Palette` is a plain `tuple[str, str, str]` and `sun_position` is `tuple[int, int] | None` — simple types with deterministic `repr`.

### New module: `application/image_hash.py`

Two functions:

**`_get_current_hash() -> str`** (private, underscore-prefixed)
- Calls `get_config()` first, then samples `datetime.datetime.now().time()` — same order as `current_image.py`
- Calls `get_current_palette(ct, cfg)` and `get_sun_position(ct, cfg)`
- Returns SHA-256 of `str((palette, sun_position, cfg["rising"].strftime("%H:%M"), cfg["setting"].strftime("%H:%M")))`

**`image_will_change() -> bool`**
- Computes current hash via `_get_current_hash()`
- Reads `/tmp/cartoon_sun_position_hash_cache`
- If cache missing or hash differs: writes new hash to cache, returns `True`
- If hash matches: returns `False`
- On any read or write error: returns `True` (safe default — better to redraw than to skip)

No `__all__` needed — existing application modules don't define it. The underscore prefix on `_get_current_hash` prevents it from being star-imported.

### Cache file

`/tmp/cartoon_sun_position_hash_cache` — plain text, one line, the SHA-256 hex digest. Follows the same `/tmp` pattern as the existing config cache.

### Export

`cartoon_sun_position/__init__.py` — add `from cartoon_sun_position.application.image_hash import *`, matching the existing star-import pattern.

## Accepted Limitations

**TOCTOU:** `image_will_change()` and `generate_image()` both call `datetime.now().time()` independently. At a palette or sun-position boundary, the two calls could land on opposite sides. Accepted — this results in an extra redraw, not a skipped one.

**Write-before-render:** The hash is written before `generate_image()` is called. If the render or display step fails, the cache holds the hash of an image never shown. During daytime the display self-corrects on the next run as the hash advances. At night — the primary use case — the hash is stable, so a failed render leaves the display stale until dawn. Accepted — render failures are rare.

## Files Changed

| File | Change |
|------|--------|
| `src/cartoon_sun_position/application/image_hash.py` | New |
| `src/cartoon_sun_position/__init__.py` | Add star import |

## Out of Scope

- No changes to `generate_image()` or the rendering pipeline
- No GIF support for change detection
- No hash persistence in adapters layer (follows existing `config.py` inline pattern)
