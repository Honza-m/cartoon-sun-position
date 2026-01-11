import datetime as dt
import os

import requests
from dotenv import load_dotenv

from cartoon_sun_position.schemas import Config


def download_config() -> Config:
    load_dotenv()
    hass_url = os.environ.get("HASS_URL")
    hass_auth_header = os.environ.get("HASS_AUTH_HEADER")
    if not hass_url or not hass_auth_header:
        raise ValueError(
            "HASS_URL and HASS_AUTH_HEADER must be set as environment variables"
        )

    date_format_s = "%Y-%m-%dT%H:%M:%S%z"
    date_format_ms = "%Y-%m-%dT%H:%M:%S.%f%z"
    r = requests.get(hass_url, headers={"Authorization": hass_auth_header})
    r.raise_for_status()
    data = next((x["attributes"] for x in r.json() if x["entity_id"] == "sun.sun"), {})
    return Config(
        dawn=dt.datetime.strptime(data["next_dawn"], date_format_ms).time(),
        dusk=dt.datetime.strptime(data["next_dusk"], date_format_ms).time(),
        midnight=dt.datetime.strptime(data["next_midnight"], date_format_s).time(),
        noon=dt.datetime.strptime(data["next_noon"], date_format_s).time(),
        rising=dt.datetime.strptime(data["next_rising"], date_format_ms).time(),
        setting=dt.datetime.strptime(data["next_setting"], date_format_ms).time(),
        valid_for=dt.datetime.strptime(data["next_dawn"], date_format_ms).date(),
    )
