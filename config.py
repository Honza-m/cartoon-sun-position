from adapters.home_assistant import download_config
from schemas import Config


def get_config() -> Config:
    return download_config()
