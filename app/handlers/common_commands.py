from aiogram import types, Dispatcher

import app.app as app


async def cmd_start(message: types.Message):
    await message.answer(f"Привет, {message.chat.username}! Я Кунжут)))")
    app.active.check_model_exists(message.chat.id)


async def cmd_help(message: types.Message):
    await message.answer("Я учусь разговаривать, запоминая ваши фразы!")


def register_commands_handlers(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands='start')
    dp.register_message_handler(cmd_help, commands='help')