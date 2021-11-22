import configparser
from dataclasses import dataclass


@dataclass
class TgBot:
    """dataclass for global bot parameters"""
    token: str


@dataclass
class IDs:
    """dataclass for admins recognising"""
    admin_id: str
    admin_group_id: str


@dataclass
class Config:
    """dataclass for config"""
    tg_bot: TgBot
    admin_ids: IDs


def load_config(path: str):
    """reads config and returns Config dataclass object"""
    config = configparser.ConfigParser()
    config.read(path)

    tg_bot = config["tg_bot"]
    ids = config["admin_ids"]

    return Config(
        tg_bot=TgBot(
            token=tg_bot["token"]
        ),
        admin_ids=IDs(
            admin_id=ids["admin_id"],
            admin_group_id=ids["admin_group_id"]
        )
    )
