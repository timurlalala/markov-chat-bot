from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext, filters
import logging
from app.app import models_active


async def cmd_start_pm(message: types.Message, state: FSMContext):
    logging.info(f'{message.chat.id} --- {message.from_user.username}')
    await state.finish()
    await message.answer(f"Привет, {message.chat.full_name}! Я Абобус.",
                         reply_markup=types.ReplyKeyboardRemove())


async def cmd_start_group(message: types.Message, state: FSMContext):
    models_active.check_model_exists(message.chat.id)
    logging.info(f'{message.chat.id} --- {message.from_user.username}')
    await state.finish()
    await message.answer(f"Привет, {message.chat.full_name}! Я Абобус.",
                         reply_markup=types.ReplyKeyboardRemove())


async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('Действие отменено', reply_markup=types.ReplyKeyboardRemove())


async def cmd_help(message: types.Message):
    await message.answer("Я учусь разговаривать, запоминая ваши фразы!")


def register_commands_handlers(dp: Dispatcher):
    dp.register_message_handler(cmd_start_pm, commands='start', state="*")
    dp.register_message_handler(cmd_start_group, commands='start', state="*")
    dp.register_message_handler(cmd_cancel, commands='cancel', state="*")
    dp.register_message_handler(cmd_help, commands='help')
