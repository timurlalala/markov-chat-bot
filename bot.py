import logging
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from app.configr_reader import load_config
from app.handlers.common_commands import register_commands_handlers
from app.handlers.dialog_behavior import register_message_handlers
from app.markov import active

logging.basicConfig(level=logging.INFO)

config = load_config("config/bot.ini")
# active = MarkovManager()
active.init_model('Aneks',
                  r'database/anecdotes.db',
                  '''SELECT anek FROM aneks ;''',
                  order=12,
                  rand_coeff=1)

active.init_model('MainChat',
                  r'database/messages.db',
                  '''SELECT message FROM texts WHERE userid = :userid''',
                  {'userid': config.admin_ids.admin_group_id})

bot = Bot(token=config.tg_bot.token)
dp = Dispatcher(bot)

register_commands_handlers(dp)
register_message_handlers(dp)

if __name__ == '__main__':
    executor.start_polling(dp)
