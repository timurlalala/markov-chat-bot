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

    models_active.init_anek_model(order=15,
                                  rand_coeff=0.0001,
                                  is_main=True)

    models_active.init_msg_model(config.admin_ids.admin_group_id,
                                 is_main=True)

    register_commands_handlers(dp)
    register_handlers_settings(dp)
    register_message_handlers(dp)

    executor.start_polling(dp)
