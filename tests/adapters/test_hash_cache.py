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
