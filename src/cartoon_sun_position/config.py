import datetime as dt
import json
from pathlib import Path

from cartoon_sun_position.adapters.home_assistant import download_config
from cartoon_sun_position.schemas import Config

CACHE_FILE = Path("/tmp/cartoon_sun_position_config_cache")


def get_config() -> Config:
    # Attempt to read from cached file if it's still valid
    if cached_config := get_cached_config():
        print("Using cached config")
        return cached_config

    # Otherwise download new config and cache it
    config = download_config()
    print("Using fresh config")
    cache_config(config)
    return config


def get_cached_config() -> Config | None:
    """Returns config cached in /tmp/ or None if it doesn't exist or is too old."""
    try:
        with open(CACHE_FILE, "r") as f:
            json_config = json.load(f)

        config = Config(
            dawn=dt.datetime.strptime(json_config["dawn"], "%H:%M:%S").time(),
            dusk=dt.datetime.strptime(json_config["dusk"], "%H:%M:%S").time(),
            midnight=dt.datetime.strptime(json_config["midnight"], "%H:%M:%S").time()
            if json_config.get("midnight")
            else None,
            noon=dt.datetime.strptime(json_config["noon"], "%H:%M:%S").time()
            if json_config.get("noon")
            else None,
            rising=dt.datetime.strptime(json_config["rising"], "%H:%M:%S").time(),
            setting=dt.datetime.strptime(json_config["setting"], "%H:%M:%S").time(),
            valid_for=dt.datetime.strptime(json_config["valid_for"], "%Y-%m-%d").date(),
        )

        return config if config["valid_for"] >= dt.date.today() else None
    except Exception:
        return None


def cache_config(config: Config):
    with open(CACHE_FILE, "w") as f:
        json.dump(
            {
                "dawn": config["dawn"].strftime("%H:%M:%S"),
                "dusk": config["dusk"].strftime("%H:%M:%S"),
                "midnight": config["midnight"].strftime("%H:%M:%S")
                if config.get("midnight")
                else None,
                "noon": config["noon"].strftime("%H:%M:%S")
                if config.get("noon")
                else None,
                "rising": config["rising"].strftime("%H:%M:%S"),
                "setting": config["setting"].strftime("%H:%M:%S"),
                "valid_for": config["valid_for"].strftime("%Y-%m-%d"),
            },
            f,
        )
