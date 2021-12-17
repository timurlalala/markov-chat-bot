import logging

from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from app.config_reader import config
from app.model import active
from app.handlers.service_commands import register_commands_handlers
from app.handlers.dialog_behavior import register_message_handlers
from app.handlers.settings import register_handlers_settings

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.tg_bot.token)
dp = Dispatcher(bot, storage=MemoryStorage())


async def run():
    logging.basicConfig(level=logging.INFO)

    active.init_model('ANEKS',
                      config.database.anecdotes_path,
                      '''SELECT anek FROM aneks ;''',
                      order=12,
                      rand_coeff=1)

    active.init_model(config.admin_ids.admin_group_id,
                      config.database.messages_path,
                      '''SELECT message FROM texts WHERE userid = :userid''',
                      {'userid': config.admin_ids.admin_group_id})

    active.init_model('PM_MODEL',
                      config.database.messages_path,
                      '''SELECT message FROM texts WHERE userid = :userid''',
                      {'userid': config.admin_ids.admin_group_id})

    register_commands_handlers(dp)
    register_handlers_settings(dp)
    register_message_handlers(dp)
    try:
        with open('/home/timursam00/markov-chat-bot/update.log', 'r') as file:
            updatelog = file.read()
    except FileNotFoundError:
        updatelog = 'there is no update log'

    await bot.send_message(chat_id=config.admin_ids.admin_id, text=updatelog)

    executor.start_polling(dp)
