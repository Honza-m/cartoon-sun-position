import hashlib
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


def _compute_image_hash(cfg, palette, sun) -> str:
    return hashlib.sha256(str((cfg, palette, sun)).encode()).hexdigest()
