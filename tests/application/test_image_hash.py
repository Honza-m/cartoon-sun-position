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
