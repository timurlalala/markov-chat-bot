import configparser
from dataclasses import dataclass


@dataclass
class TgBot:
    """dataclass for global bot parameters"""
    token: str


@dataclass
class ID:
    """dataclass for admins recognising"""
    admin_id: int
    admin_group_id: int


@dataclass
class DataBasePath:
    """dataclass for paths for databases"""
    messages_path: str
    anecdotes_path: str


@dataclass
class Config:
    """dataclass for config"""
    tg_bot: TgBot
    admin_ids: ID
    database: DataBasePath


def load_config(path: str):
    """reads config and returns Config dataclass object"""
    config = configparser.ConfigParser()
    config.read(path)

    tg_bot = config["tg_bot"]
    admin_ids = config["admin_ids"]
    database = config["database"]

    return Config(
        tg_bot=TgBot(
            token=tg_bot["token"]
        ),
        admin_ids=ID(
            admin_id=int(admin_ids["admin_id"]),
            admin_group_id=int(admin_ids["admin_group_id"])
        ),
        database=DataBasePath(
            messages_path=database["messages_path"],
            anecdotes_path=database["anecdotes_path"]
        )
    )

config = load_config("config/bot.ini")