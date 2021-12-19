import logging

from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from app.config_reader import config
from app.model import models_active
from app.handlers.service_commands import register_commands_handlers
from app.handlers.dialog_behavior import register_message_handlers
from app.handlers.settings import register_handlers_settings

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.tg_bot.token)
dp = Dispatcher(bot, storage=MemoryStorage())


def run():
    logging.basicConfig(level=logging.INFO)

    models_active.init_model('ANEKS',
                             config.database.anecdotes_path,
                             '''SELECT anek FROM aneks ;''',
                             last_text_enabled=False,
                             order=12,
                             rand_coeff=1,
                             is_main=True)

    models_active.init_model(config.admin_ids.admin_group_id,
                             config.database.messages_path,
                             '''SELECT message FROM texts WHERE userid = :userid''',
                             {'userid': config.admin_ids.admin_group_id},
                             is_main=True)

    models_active.init_model('PM_MODEL',
                             config.database.messages_path,
                             '''SELECT message FROM texts WHERE userid = :userid''',
                             {'userid': config.admin_ids.admin_group_id},
                             is_main=True)

    register_commands_handlers(dp)
    register_handlers_settings(dp)
    register_message_handlers(dp)

    executor.start_polling(dp)
