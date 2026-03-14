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

- **Deep night** (`ct < cfg["dawn"] or ct >= cfg["dusk"]`): palette is `NIGHT_COLOUR` (fixed constant), sun position is `None` → stable hash, `image_will_change()` returns `False` → display skipped. Note: `get_sun_position()` uses `ct > cfg["setting"]` (strict `>`), while `get_current_palette()` uses `ct >= cfg["dusk"]`. These boundaries don't coincide — between `setting` and `dusk` both are still changing. The stable-night claim holds for the bulk of the night window where the conditions overlap.
- **Midnight config rollover:** the config cache invalidates at midnight, fetching new values. The full-config hash will differ and `image_will_change()` correctly returns `True`.
- **Daytime**: sun position changes continuously (integer-truncated `(x, y)`), so the hash changes on most runs. At slow-moving extremes near rise/set, coordinates could be identical across runs — a minor false negative skipping a negligible redraw. Expected.
- **Twilight / low-sun windows**: palette transitions through multiple steps, hash changes. Expected.

The primary benefit is eliminating unnecessary display redraws during the night.

## Design

### Hash inputs

The hash covers the **entire `Config`** (since it is fully passed to `generate_image()`), plus `palette` and `sun_position`:

- `cfg` — all fields: `dawn`, `dusk`, `midnight`, `noon`, `rising`, `setting`, `valid_for`
- `palette` — `tuple[str, str, str]` from `get_current_palette()`
- `sun_position` — `tuple[int, int] | None` from `get_sun_position()`

Hash: `SHA-256(str((cfg, palette, sun_position)))`. `str()` is stable: `Config` is a `TypedDict` so `str(cfg)` produces a dict repr whose insertion order is stable in Python 3.7+. All values are `dt.time`, `dt.date`, or `None` — simple types with deterministic `repr`. Same for `Palette` (`tuple[str, str, str]`) and `Coor` (`tuple[int, int] | None`).

### Shared adapter: `adapters/hash_cache.py`

Both `image_will_change()` and `generate_image()` need access to the hash cache. The file I/O is extracted into a new adapter following the existing adapter pattern:

- `read_hash() -> str | None` — reads `/tmp/cartoon_sun_position_hash_cache`, returns the stored hex digest or `None` on any error
- `write_hash(digest: str)` — writes the hex digest to `/tmp/cartoon_sun_position_hash_cache`, silently ignores write errors

### New module: `application/image_hash.py`

One function:

**`image_will_change() -> bool`**
- Calls `get_config()`, then `ct = datetime.datetime.now().time()` (same order as `current_image.py`)
- Computes `palette`, `sun_position`, and hash (`SHA-256(str((cfg, palette, sun_position)))`)
- Reads stored hash via `adapters/hash_cache.read_hash()`
- Returns `True` if stored hash is `None` or differs from current hash
- Returns `False` if hashes match
- Does **not** write the hash — that is `generate_image()`'s responsibility

### Updated: `application/current_image.py`

`generate_image()` gains one responsibility after rendering:

- Before returning, at the end of the function body, calls `adapters/hash_cache.write_hash(digest)` with the same hash inputs used by `image_will_change()`
- Hash computation is duplicated minimally in both modules (same three lines: palette, sun, digest). No shared helper needed — the inputs are already computed as part of each function's normal flow.

### Export

`cartoon_sun_position/__init__.py` — add `from cartoon_sun_position.application.image_hash import *`, matching the existing star-import pattern.

## Accepted Limitations

**TOCTOU:** `image_will_change()` and `generate_image()` both call `datetime.now().time()` independently. At a palette or sun-position boundary, the two calls could land on opposite sides, producing a mismatched hash written to cache. Accepted — this results in at most one extra redraw on the next run, not a skipped one.

## Files Changed

| File | Change |
|------|--------|
| `src/cartoon_sun_position/adapters/hash_cache.py` | New |
| `src/cartoon_sun_position/application/image_hash.py` | New |
| `src/cartoon_sun_position/application/current_image.py` | Write hash after render |
| `src/cartoon_sun_position/__init__.py` | Add star import |

## Out of Scope

- No changes to `generate_image()`'s return value or rendering pipeline
- No GIF support for change detection
