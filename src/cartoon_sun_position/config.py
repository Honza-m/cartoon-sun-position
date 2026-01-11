from cartoon_sun_position.adapters.home_assistant import download_config
from cartoon_sun_position.schemas import Config


def get_config() -> Config:
    return download_config()
