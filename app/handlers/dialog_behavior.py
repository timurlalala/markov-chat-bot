from aiogram import types, Dispatcher
from aiogram.dispatcher import filters
from aiogram.utils import exceptions

from app.app import active, config
import database.db as db


async def command_anek(message: types.Message):
    text = active.models['Aneks'].generate_l()
    await message.bot.send_message(chat_id=message.chat.id, text=text)


async def message_processing_mainchat(message: types.Message):
    db.insert_or_update(userid=message.chat.id, message=message.text)
    active.models[message.chat.id].parse_and_add(text=message.text)
    text = active.models[message.chat.id].generate_answer(message=message.text)
    try:
        await message.bot.send_message(chat_id=message.chat.id, text=text)
    except exceptions.MessageTextIsEmpty:
        return


async def message_processing_group(message: types.Message):
    db.insert_or_update(userid=message.chat.id, message=message.text)
    try:
        active.models[message.chat.id].parse_and_add(text=message.text)
    except KeyError:
        active.check_model_exists(message.chat.id)
    text = active.models[message.chat.id].generate_answer(message=message.text)
    try:
        await message.bot.send_message(chat_id=message.chat.id, text=text)
    except exceptions.MessageTextIsEmpty:
        return


async def message_processing_pm(message: types.Message):
    db.insert_or_update(userid=message.chat.id, message=message.text)
    text = active.models[config.admin_ids.admin_group_id].generate_answer(message=message.text)
    await message.bot.send_message(chat_id=message.chat.id, text=text)


def register_message_handlers(dp: Dispatcher):
    dp.register_message_handler(command_anek, commands='anek')
    dp.register_message_handler(message_processing_mainchat,
                                filters.IDFilter(chat_id=config.admin_ids.admin_group_id))
    dp.register_message_handler(message_processing_group, filters.ChatTypeFilter(types.ChatType.GROUP))
    dp.register_message_handler(message_processing_pm, filters.ChatTypeFilter(types.ChatType.PRIVATE))
