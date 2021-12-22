import logging

from aiogram import types, Dispatcher
from aiogram.dispatcher import filters
from aiogram.utils import exceptions
from time import time
from app.app import models_active, config
import database.db_manager as db


async def command_anek(message: types.Message):
    text = models_active.models['ANEKS'].generate_l()
    await message.bot.send_message(chat_id=message.chat.id, text=text)


async def message_processing_mainchat(message: types.Message):
    try:
        text = models_active.models[message.chat.id].generate_answer(message=message.text)
        models_active.models[message.chat.id].last_answer = None
    except IndexError:
        text = 'Недостаточно данных для генерациии сообщений.\
                \nБот учится на ваших сообщениях, напишите что-нибудь!'
    models_active.models[message.chat.id].parse_and_add(text=message.text)
    db.msg_insert_or_update(chatid=message.chat.id,
                            userid=message.from_user.id,
                            message=message.text,
                            timestamp=time(),
                            last_ans=models_active.models[message.chat.id].last_answer)
    try:
        await message.bot.send_message(chat_id=message.chat.id, text=text)
    except exceptions.MessageTextIsEmpty:
        return


async def message_processing_mainchat_replied(message: types.Message):
    try:
        text = models_active.models[message.chat.id].generate_answer(message=message.text, answer_chance=1)
        models_active.models[message.chat.id].last_answer = message\
                                                                .reply_to_message\
                                                                .text[models_active.models[message.chat.id].N:]
    except IndexError:
        text = 'Недостаточно данных для генерациии сообщений.\
                \nБот учится на ваших сообщениях, напишите что-нибудь!'
    models_active.models[message.chat.id].parse_and_add(text=message.text)
    db.msg_insert_or_update(chatid=message.chat.id,
                            userid=message.from_user.id,
                            message=message.text,
                            timestamp=time(),
                            last_ans=models_active.models[message.chat.id].last_answer)
    try:
        await message.bot.send_message(chat_id=message.chat.id, text=text)
    except exceptions.MessageTextIsEmpty:
        return


async def message_processing_group(message: types.Message):
    try:
        models_active.models[message.chat.id]
    except KeyError:
        models_active.check_model_exists(message.chat.id)
    try:
        text = models_active.models[message.chat.id].generate_answer(message=message.text)
        models_active.models[message.chat.id].last_answer = None
    except IndexError:
        text = 'Недостаточно данных для генерациии сообщений.\
                \nБот учится на ваших сообщениях, напишите что-нибудь!'
    models_active.models[message.chat.id].parse_and_add(text=message.text)
    db.msg_insert_or_update(chatid=message.chat.id,
                            userid=message.from_user.id,
                            message=message.text,
                            timestamp=time(),
                            last_ans=models_active.models[message.chat.id].last_answer)
    try:
        await message.bot.send_message(chat_id=message.chat.id, text=text)
    except exceptions.MessageTextIsEmpty:
        return


async def message_processing_group_replied(message: types.Message):
    try:
        models_active.models[message.chat.id]
    except KeyError:
        models_active.check_model_exists(message.chat.id)
    try:
        text = models_active.models[message.chat.id].generate_answer(message=message.text, answer_chance=1)
        models_active.models[message.chat.id].last_answer = message\
                                                                .reply_to_message\
                                                                .text[models_active.models[message.chat.id].N:]
    except IndexError:
        text = 'Недостаточно данных для генерациии сообщений.\
                \nБот учится на ваших сообщениях, напишите что-нибудь!'
    models_active.models[message.chat.id].parse_and_add(text=message.text)
    logging.info(message.reply_to_message.text)
    db.msg_insert_or_update(chatid=message.chat.id,
                            userid=message.from_user.id,
                            message=message.text,
                            timestamp=time(),
                            last_ans=models_active.models[message.chat.id].last_answer)
    try:
        await message.bot.send_message(chat_id=message.chat.id, text=text)
    except exceptions.MessageTextIsEmpty:
        return


async def message_processing_pm(message: types.Message):
    text = models_active.models[config.admin_ids.admin_group_id].generate_answer(message=message.text,
                                                                                 answer_chance=1,
                                                                                 rand_coeff=10)
    await message.bot.send_message(chat_id=message.chat.id, text=text)


def register_message_handlers(dp: Dispatcher):
    dp.register_message_handler(command_anek, commands='anek')
    dp.register_message_handler(message_processing_mainchat_replied,
                                filters.IsReplyFilter(True),
                                filters.IDFilter(chat_id=config.admin_ids.admin_group_id))
    dp.register_message_handler(message_processing_mainchat,
                                filters.IDFilter(chat_id=config.admin_ids.admin_group_id))
    dp.register_message_handler(message_processing_group_replied,
                                filters.ChatTypeFilter(types.ChatType.GROUP),
                                filters.IsReplyFilter(True))
    dp.register_message_handler(message_processing_group, filters.ChatTypeFilter(types.ChatType.GROUP))
    dp.register_message_handler(message_processing_pm, filters.ChatTypeFilter(types.ChatType.PRIVATE))
