from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import app.app as app


class SettingsMenu(StatesGroup):
    waiting_for_option = State()
    waiting_for_ans_chance = State()
    waiting_for_rand_coeff = State()


options = ('answer_chance', 'rand_coeff', '/cancel')


async def settings_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, selective=True)
    for option in options:
        keyboard.add(option)
    await message.reply('Какой параметр изменить?', reply_markup=keyboard)
    await SettingsMenu.waiting_for_option.set()


async def option_chosen(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, selective=True)
    keyboard.add('/cancel')
    if message.text.lower() == 'answer_chance':
        await message.reply('Введите значение в процентах, по умолчанию 100', reply_markup=keyboard)
        await SettingsMenu.waiting_for_ans_chance.set()
    elif message.text.lower() == 'rand_coeff':
        await message.reply('Введите значение в процентах, по умолчанию 1', reply_markup=keyboard)
        await SettingsMenu.waiting_for_rand_coeff.set()
    else:
        await message.reply('Выберите параметр из предложенных ниже.')
        return


async def set_ac(message: types.Message, state: FSMContext):
    try:
        text = app.active.models[message.chat.id].set_answer_chance(int(message.text))
    except KeyError:
        app.active.check_model_exists(message.chat.id)
        text = app.active.models[message.chat.id].set_answer_chance(int(message.text))
    await message.reply(text, reply_markup=types.ReplyKeyboardRemove())
    await state.finish()


async def set_rc(message: types.Message, state: FSMContext):
    try:
        text = app.active.models[message.chat.id].set_rand_coeff(int(message.text))
    except KeyError:
        app.active.check_model_exists(message.chat.id)
        text = app.active.models[message.chat.id].set_answer_chance(int(message.text))
    await message.reply(text, reply_markup=types.ReplyKeyboardRemove())
    await state.finish()


def register_handlers_settings(dp: Dispatcher):
    dp.register_message_handler(settings_start, commands="settings", state="*")
    dp.register_message_handler(option_chosen, state=SettingsMenu.waiting_for_option)
    dp.register_message_handler(set_rc, state=SettingsMenu.waiting_for_rand_coeff)
    dp.register_message_handler(set_ac, state=SettingsMenu.waiting_for_ans_chance)