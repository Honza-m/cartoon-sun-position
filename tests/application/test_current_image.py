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
