import logging

from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

from app.config_reader import load_config
from app.handlers.service_commands import register_commands_handlers
from app.handlers.dialog_behavior import register_message_handlers
from app.model import Manager

logging.basicConfig(level=logging.INFO)

config = load_config("config/bot.ini")

bot = Bot(token=config.tg_bot.token)
dp = Dispatcher(bot)

active = Manager()


def run():
    logging.basicConfig(level=logging.INFO)

    active.init_model('Aneks',
                      r'database/anecdotes.db',
                      '''SELECT anek FROM aneks ;''',
                      order=12,
                      rand_coeff=1)

    active.init_model(config.admin_ids.admin_group_id,
                      r'database/messages.db',
                      '''SELECT message FROM texts WHERE userid = :userid''',
                      {'userid': config.admin_ids.admin_group_id})

    register_commands_handlers(dp)
    register_message_handlers(dp)

    executor.start_polling(dp)
