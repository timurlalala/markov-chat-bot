from aiogram import types, Dispatcher

import app.app as app


async def cmd_start(message: types.Message):
    app.active.check_model_exists(message.chat.id)
    await message.answer(f"Привет, {message.from_user.username}! Я Abobus)))")


async def cmd_help(message: types.Message):
    await message.answer("Я учусь разговаривать, запоминая ваши фразы!")


def register_commands_handlers(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands='start')
    dp.register_message_handler(cmd_help, commands='help')