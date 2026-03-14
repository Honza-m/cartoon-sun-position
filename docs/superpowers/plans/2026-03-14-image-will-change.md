# image_will_change Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `image_will_change() -> bool` so the calling script can skip re-rendering the e-ink display when the image hasn't changed (primarily at night).

**Architecture:** A new `adapters/hash_cache.py` handles reading/writing the hash from `/tmp`. A new `application/image_hash.py` exposes `image_will_change()`, which computes a hash of the current render inputs and compares against the stored hash. `generate_image()` in `current_image.py` writes the hash just before returning — so the hash is only committed after a successful render.

**Tech Stack:** Python 3.13, pytest (new dev dependency), `hashlib` (stdlib), `unittest.mock` (stdlib).

---

## Chunk 1: Test infrastructure + hash cache adapter

### Task 1: Add pytest as a dev dependency

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Add `[project.optional-dependencies]` section to `pyproject.toml`**

Open `pyproject.toml` and add after the `[project]` dependencies list (before `[build-system]`):

```toml
[project.optional-dependencies]
dev = ["pytest>=8.0"]
```

- [ ] **Step 2: Install dev dependencies**

```bash
uv sync --extra dev
```

Expected: resolves and installs pytest.

- [ ] **Step 3: Verify pytest runs**

```bash
uv run --extra dev pytest --collect-only
```

Expected: exit code 5 ("no tests collected") — this is correct at this stage, no tests exist yet.

---

### Task 2: Create test directory structure

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/adapters/__init__.py`
- Create: `tests/application/__init__.py` (used in Chunk 2)

- [ ] **Step 1: Create the test directories and empty `__init__.py` files**

```bash
mkdir -p tests/adapters tests/application
touch tests/__init__.py tests/adapters/__init__.py tests/application/__init__.py
```

- [ ] **Step 2: Verify structure**

```bash
find tests -type f
```

Expected:
```
tests/__init__.py
tests/adapters/__init__.py
tests/application/__init__.py
```

---

### Task 3: Create `adapters/hash_cache.py` — TDD

**Files:**
- Create: `tests/adapters/test_hash_cache.py`
- Create: `src/cartoon_sun_position/adapters/hash_cache.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/adapters/test_hash_cache.py`:

```python
from unittest.mock import patch

from cartoon_sun_position.adapters.hash_cache import read_hash, write_hash


def test_read_hash_returns_none_when_file_missing():
    with patch("cartoon_sun_position.adapters.hash_cache.HASH_CACHE_FILE") as mock_path:
        mock_path.read_text.side_effect = FileNotFoundError
        assert read_hash() is None


def test_read_hash_returns_stored_digest():
    digest = "abc123def456"
    with patch("cartoon_sun_position.adapters.hash_cache.HASH_CACHE_FILE") as mock_path:
        mock_path.read_text.return_value = digest
        assert read_hash() == digest


def test_read_hash_returns_none_on_any_error():
    with patch("cartoon_sun_position.adapters.hash_cache.HASH_CACHE_FILE") as mock_path:
        mock_path.read_text.side_effect = OSError("disk full")
        assert read_hash() is None


def test_write_hash_writes_digest():
    digest = "abc123def456"
    with patch("cartoon_sun_position.adapters.hash_cache.HASH_CACHE_FILE") as mock_path:
        write_hash(digest)
        mock_path.write_text.assert_called_once_with(digest)


def test_write_hash_ignores_write_errors():
    with patch("cartoon_sun_position.adapters.hash_cache.HASH_CACHE_FILE") as mock_path:
        mock_path.write_text.side_effect = OSError("read only")
        write_hash("abc123")  # must not raise
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run --extra dev pytest tests/adapters/test_hash_cache.py -v
```

Expected: `ModuleNotFoundError` or `ImportError` — `hash_cache` doesn't exist yet.

- [ ] **Step 3: Implement `adapters/hash_cache.py`**

Create `src/cartoon_sun_position/adapters/hash_cache.py`:

Note: `/tmp` follows the established pattern in this project — `config.py` already uses `Path("/tmp/cartoon_sun_position_config_cache")`.

```python
from pathlib import Path

HASH_CACHE_FILE = Path("/tmp/cartoon_sun_position_hash_cache")


def read_hash() -> str | None:
    try:
        return HASH_CACHE_FILE.read_text()
    except Exception:
        return None


def write_hash(digest: str) -> None:
    try:
        HASH_CACHE_FILE.write_text(digest)
    except Exception:
        pass
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run --extra dev pytest tests/adapters/test_hash_cache.py -v
```

Expected: 5 passed.

- [ ] **Step 5: Commit**

Note: `src/cartoon_sun_position/adapters/__init__.py` is already tracked by git — no need to add it.

```bash
git add pyproject.toml tests/ src/cartoon_sun_position/adapters/hash_cache.py
git commit -m "feat: add hash cache adapter and test infrastructure"
```

---

## Chunk 2: image_will_change + generate_image update + export

### Task 4: Create `application/image_hash.py` — TDD

**Files:**
- Create: `tests/application/test_image_hash.py`
- Create: `src/cartoon_sun_position/application/image_hash.py`

The hash is `SHA-256(str((cfg, palette, sun_position)).encode()).hexdigest()`. All three inputs are mocked in tests, so computing the expected digest in the test is straightforward.

- [ ] **Step 1: Write the failing tests**

Create `tests/application/test_image_hash.py`:

```python
import datetime as dt
import hashlib
from unittest.mock import patch

from cartoon_sun_position.application.image_hash import image_will_change

CFG = {
    "dawn": dt.time(6, 0),
    "dusk": dt.time(20, 0),
    "midnight": None,
    "noon": None,
    "rising": dt.time(7, 0),
    "setting": dt.time(19, 0),
    "valid_for": dt.date(2026, 3, 14),
}
PALETTE = ("#6B7C7A", "#9FAFA8", "#DCE6DD")
SUN = (100, 200)
DIGEST = hashlib.sha256(str((CFG, PALETTE, SUN)).encode()).hexdigest()


def test_image_will_change_returns_true_when_no_cache():
    with (
        patch("cartoon_sun_position.application.image_hash.get_config", return_value=CFG),
        patch("cartoon_sun_position.application.image_hash.get_current_palette", return_value=PALETTE),
        patch("cartoon_sun_position.application.image_hash.get_sun_position", return_value=SUN),
        patch("cartoon_sun_position.application.image_hash.read_hash", return_value=None),
    ):
        assert image_will_change() is True


def test_image_will_change_returns_false_when_hash_matches():
    with (
        patch("cartoon_sun_position.application.image_hash.get_config", return_value=CFG),
        patch("cartoon_sun_position.application.image_hash.get_current_palette", return_value=PALETTE),
        patch("cartoon_sun_position.application.image_hash.get_sun_position", return_value=SUN),
        patch("cartoon_sun_position.application.image_hash.read_hash", return_value=DIGEST),
    ):
        assert image_will_change() is False


def test_image_will_change_returns_true_when_hash_differs():
    with (
        patch("cartoon_sun_position.application.image_hash.get_config", return_value=CFG),
        patch("cartoon_sun_position.application.image_hash.get_current_palette", return_value=PALETTE),
        patch("cartoon_sun_position.application.image_hash.get_sun_position", return_value=SUN),
        patch("cartoon_sun_position.application.image_hash.read_hash", return_value="stale_hash"),
    ):
        assert image_will_change() is True


def test_image_will_change_returns_false_when_sun_is_none_and_hash_matches():
    """At night sun_position is None — hash should be stable and detectable."""
    night_digest = hashlib.sha256(str((CFG, PALETTE, None)).encode()).hexdigest()
    with (
        patch("cartoon_sun_position.application.image_hash.get_config", return_value=CFG),
        patch("cartoon_sun_position.application.image_hash.get_current_palette", return_value=PALETTE),
        patch("cartoon_sun_position.application.image_hash.get_sun_position", return_value=None),
        patch("cartoon_sun_position.application.image_hash.read_hash", return_value=night_digest),
    ):
        assert image_will_change() is False
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run --extra dev pytest tests/application/test_image_hash.py -v
```

Expected: `ImportError` — `image_hash` doesn't exist yet.

- [ ] **Step 3: Implement `application/image_hash.py`**

Create `src/cartoon_sun_position/application/image_hash.py`:

```python
import datetime as dt
import hashlib

from cartoon_sun_position.adapters.hash_cache import read_hash
from cartoon_sun_position.config import get_config
from cartoon_sun_position.services.palettes import get_current_palette
from cartoon_sun_position.services.sun import get_sun_position


def image_will_change() -> bool:
    cfg = get_config()
    ct = dt.datetime.now().time()
    palette = get_current_palette(ct, cfg)
    sun = get_sun_position(ct, cfg)
    digest = hashlib.sha256(str((cfg, palette, sun)).encode()).hexdigest()
    stored = read_hash()
    return stored is None or stored != digest
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run --extra dev pytest tests/application/test_image_hash.py -v
```

Expected: 4 passed.

---

### Task 5: Update `generate_image()` to write the hash — TDD

**Files:**
- Create: `tests/application/test_current_image.py`
- Modify: `src/cartoon_sun_position/application/current_image.py`

- [ ] **Step 1: Write the failing test**

Create `tests/application/test_current_image.py`:

```python
import datetime as dt
import hashlib
from unittest.mock import MagicMock, patch

from cartoon_sun_position.application.current_image import generate_image

CFG = {
    "dawn": dt.time(6, 0),
    "dusk": dt.time(20, 0),
    "midnight": None,
    "noon": None,
    "rising": dt.time(7, 0),
    "setting": dt.time(19, 0),
    "valid_for": dt.date(2026, 3, 14),
}
PALETTE = ("#6B7C7A", "#9FAFA8", "#DCE6DD")
SUN = (100, 200)


def test_generate_image_writes_hash_before_returning():
    expected_digest = hashlib.sha256(str((CFG, PALETTE, SUN)).encode()).hexdigest()
    mock_image = MagicMock()

    with (
        patch("cartoon_sun_position.application.current_image.get_config", return_value=CFG),
        patch("cartoon_sun_position.application.current_image.get_current_palette", return_value=PALETTE),
        patch("cartoon_sun_position.application.current_image.get_sun_position", return_value=SUN),
        patch("cartoon_sun_position.application.current_image.get_base_image", return_value=mock_image),
        patch("cartoon_sun_position.application.current_image.add_sunrise_sunset_info", return_value=mock_image),
        patch("cartoon_sun_position.application.current_image.write_hash") as mock_write,
    ):
        result = generate_image()

    mock_write.assert_called_once_with(expected_digest)
    assert result is mock_image
```

- [ ] **Step 2: Run test to verify it fails**

```bash
uv run --extra dev pytest tests/application/test_current_image.py -v
```

Expected: FAIL — `write_hash` not imported or called.

- [ ] **Step 3: Update `current_image.py`**

Open `src/cartoon_sun_position/application/current_image.py` and apply these changes:

```python
import datetime as dt
import hashlib

from PIL import Image

from cartoon_sun_position.adapters.hash_cache import write_hash
from cartoon_sun_position.adapters.output import save_image
from cartoon_sun_position.config import get_config
from cartoon_sun_position.services.image import add_sunrise_sunset_info, get_base_image
from cartoon_sun_position.services.palettes import get_current_palette
from cartoon_sun_position.services.sun import get_sun_position


def generate_image() -> Image.Image:
    print("Getting configuration and current time")
    cfg = get_config()
    ct = dt.datetime.now().time()

    print("Generating color palette and sun position")
    palette = get_current_palette(ct, cfg)
    sun = get_sun_position(ct, cfg)

    print("Creating image")
    image = get_base_image(palette, sun)
    image = add_sunrise_sunset_info(image, cfg)

    digest = hashlib.sha256(str((cfg, palette, sun)).encode()).hexdigest()
    write_hash(digest)

    return image


def generate_to_file():
    image = generate_image()
    save_image(image)
    print("Image saved successfully")
```

- [ ] **Step 4: Run test to verify it passes**

```bash
uv run --extra dev pytest tests/application/test_current_image.py -v
```

Expected: 1 passed.

- [ ] **Step 5: Run full test suite**

```bash
uv run --extra dev pytest -v
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add tests/application/ src/cartoon_sun_position/application/
git commit -m "feat: image_will_change and generate_image hash writing"
```

---

### Task 6: Export `image_will_change` from package

**Files:**
- Modify: `src/cartoon_sun_position/__init__.py`

- [ ] **Step 1: Add star import to `__init__.py`**

Open `src/cartoon_sun_position/__init__.py` and add the new import:

```python
from cartoon_sun_position.application.current_image import *
from cartoon_sun_position.application.gif import *
from cartoon_sun_position.application.image_hash import *
```

- [ ] **Step 2: Verify the export is accessible**

```bash
uv run python -c "from cartoon_sun_position import image_will_change; print(image_will_change)"
```

Expected: `<function image_will_change at 0x...>`

- [ ] **Step 3: Commit**

```bash
git add src/cartoon_sun_position/__init__.py
git commit -m "feat: export image_will_change from package"
```
