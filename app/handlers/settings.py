from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext, filters
from aiogram.dispatcher.filters.state import State, StatesGroup
from app.app import active, config
import subprocess


class GroupSettingsMenu(StatesGroup):
    gsm_waiting_for_option = State()
    gsm_waiting_for_ans_chance = State()
    gsm_waiting_for_rand_coeff = State()


class AdminSettingsMenu(StatesGroup):
    asm_waiting_for_option = State()


gsm_options = ('answer_chance', 'rand_coeff', '/cancel')
asm_options = ('update bot', 'status', 'last update log', '/cancel')


async def gsm_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, selective=True)
    for option in gsm_options:
        keyboard.add(option)
    await message.reply('Какой параметр изменить?', reply_markup=keyboard)
    await GroupSettingsMenu.gsm_waiting_for_option.set()


async def gsm_option_chosen(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, selective=True)
    keyboard.add('/cancel')
    if message.text.lower() == 'answer_chance':
        await message.reply('Введите значение в процентах, по умолчанию 100', reply_markup=keyboard)
        await GroupSettingsMenu.gsm_waiting_for_ans_chance.set()
    elif message.text.lower() == 'rand_coeff':
        await message.reply('Введите значение в процентах, по умолчанию 1', reply_markup=keyboard)
        await GroupSettingsMenu.gsm_waiting_for_rand_coeff.set()
    else:
        await message.reply('Выберите параметр из предложенных ниже.')
        return


async def gsm_set_ac(message: types.Message, state: FSMContext):
    try:
        text = active.models[message.chat.id].set_answer_chance(int(message.text))
    except KeyError:
        active.check_model_exists(message.chat.id)
        text = active.models[message.chat.id].set_answer_chance(int(message.text))
    await message.reply(text, reply_markup=types.ReplyKeyboardRemove())
    await state.finish()


async def gsm_set_rc(message: types.Message, state: FSMContext):
    try:
        text = active.models[message.chat.id].set_rand_coeff(int(message.text))
    except KeyError:
        active.check_model_exists(message.chat.id)
        text = active.models[message.chat.id].set_answer_chance(int(message.text))
    await message.reply(text, reply_markup=types.ReplyKeyboardRemove())
    await state.finish()


async def asm_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, selective=True)
    for option in asm_options:
        keyboard.add(option)
    await message.reply('Выбери опцию', reply_markup=keyboard)
    await AdminSettingsMenu.asm_waiting_for_option.set()


async def asm_option_chosen(message: types.Message, state: FSMContext):
    if message.text.lower() == 'update bot':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                             one_time_keyboard=True,
                                             selective=True)
        keyboard.add('last update log')
        await message.reply('Запрашиваю обновления', reply_markup=keyboard)
        await state.finish()
        subprocess.run('/home/timursam00/markov-chat-bot/update', shell=True, capture_output=True)
    elif message.text.lower() == 'status':
        result = subprocess.run(['systemctl', 'status markovbot'], capture_output=True)
        text = result.stdout.decode('utf-8')
        await message.reply(text, reply_markup=types.ReplyKeyboardRemove())
        await state.finish()
    else:
        await message.reply('Выберите опцию из предложенных ниже.')
        return


async def asm_update_log(message: types.Message):
    try:
        with open('/home/timursam00/markov-chat-bot/update.log', 'r') as file:
            updatelog = file.read()
    except FileNotFoundError:
        updatelog = 'there is no update log'

    await message.answer(text=updatelog, reply_markup=types.ReplyKeyboardRemove())


def register_handlers_settings(dp: Dispatcher):

    dp.register_message_handler(asm_start,
                                filters.IDFilter(config.admin_ids.admin_id),
                                commands="settings",
                                state="*")
    dp.register_message_handler(asm_option_chosen,
                                state=AdminSettingsMenu.asm_waiting_for_option)
    dp.register_message_handler(asm_update_log,
                                filters.IDFilter(config.admin_ids.admin_id),
                                filters.Text('last update log'),
                                state="*")

    dp.register_message_handler(gsm_start,
                                filters.ChatTypeFilter(types.ChatType.GROUP),
                                commands="settings",
                                state="*")
    dp.register_message_handler(gsm_option_chosen,
                                state=GroupSettingsMenu.gsm_waiting_for_option)
    dp.register_message_handler(gsm_set_rc,
                                state=GroupSettingsMenu.gsm_waiting_for_rand_coeff)
    dp.register_message_handler(gsm_set_ac,
                                state=GroupSettingsMenu.gsm_waiting_for_ans_chance)
