# Design: `image_will_change()` — Skip Re-render When Image Is Unchanged

**Date:** 2026-03-14

## Problem

The tool runs on a cron schedule and always calls `generate_image()` + redraws the e-ink display, even when nothing has changed (e.g. at night, when the sun is below the horizon and the image is identical every run).

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

## Why This Works for Night Skipping

At night (`ct < cfg["rising"] or ct > cfg["setting"]`), `get_sun_position()` returns `None` and `get_current_palette()` returns the fixed `NIGHT_COLOUR` constant. The hash is therefore identical on every cron run during the night → `image_will_change()` returns `False` → no redraw.

## Design

### New module: `application/image_hash.py`

Two functions:

**`_get_current_hash() -> str`**
- Calls `get_config()`, `get_current_palette(ct, cfg)`, `get_sun_position(ct, cfg)`
- Returns SHA-256 of `str((palette, sun_position))`
- Uses `datetime.datetime.now().time()` for current time (same as `current_image.py`)

**`image_will_change() -> bool`**
- Reads `/tmp/cartoon_sun_position_hash_cache`
- Computes current hash via `_get_current_hash()`
- If cache missing or hash differs: writes new hash to cache, returns `True`
- If hash matches: returns `False`
- On any read error: returns `True` (safe default — better to redraw than to skip)

### Cache file

`/tmp/cartoon_sun_position_hash_cache` — plain text, one line, the SHA-256 hex digest. Follows the same `/tmp` pattern as the existing config cache.

### Export

`cartoon_sun_position/__init__.py` — add `image_will_change` to exports alongside `generate_image`.

## Files Changed

| File | Change |
|------|--------|
| `src/cartoon_sun_position/application/image_hash.py` | New |
| `src/cartoon_sun_position/__init__.py` | Add export |

## Out of Scope

- No changes to `generate_image()` or the rendering pipeline
- No GIF support for change detection
- No hash persistence in adapters layer (follows existing `config.py` inline pattern)
