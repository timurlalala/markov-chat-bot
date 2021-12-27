from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext, filters
from aiogram.dispatcher.filters.state import State, StatesGroup
from app.app import models_active, config
import subprocess


class GroupSettingsMenu(StatesGroup):
    """states for settings in groups"""
    gsm_wait_for_option = State()
    gsm_wait_for_ans_chance = State()
    gsm_wait_for_rand_coeff = State()


class AdminSettingsMenu(StatesGroup):
    """states for managing bot via admin pm chat"""
    asm_wait_for_option = State()
    asm_wait_for_anek_option = State()
    asm_wait_for_anek_rand_coeff = State()
    asm_wait_for_anek_order = State()


gsm_options = ('answer_chance', 'rand_coeff', '*показать_параметры*', '/cancel')
asm_start_options = ('*update bot*',
                     '*show status*',
                     '*last update log*',
                     '*aneks settings*',
                     '/cancel')
asm_anek_options = ('rand_coeff', 'order', '*показать параметры*', '*dump*', '/cancel')


# handlers for group chat settings
async def gsm_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, selective=True)
    for option in gsm_options:
        keyboard.add(option)
    await message.reply('Какой параметр изменить?', reply_markup=keyboard)
    await GroupSettingsMenu.gsm_wait_for_option.set()


async def gsm_ac_chosen(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, selective=True)
    keyboard.add('/cancel')
    await message.reply('Введите значение в процентах, по умолчанию 100', reply_markup=keyboard)
    await GroupSettingsMenu.gsm_wait_for_ans_chance.set()


async def gsm_rc_chosen(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, selective=True)
    keyboard.add('/cancel')
    await message.reply('Введите значение в процентах, по умолчанию 1', reply_markup=keyboard)
    await GroupSettingsMenu.gsm_wait_for_rand_coeff.set()


async def wrong_opt_chosen(message: types.Message, state: FSMContext):
    await message.reply('Выберите параметр из предложенных ниже.')


async def gsm_set_ac(message: types.Message, state: FSMContext):
    try:
        text = models_active.models[message.chat.id].set_answer_chance(float(message.text))
    except KeyError:
        models_active.check_model_exists(message.chat.id)
        text = models_active.models[message.chat.id].set_answer_chance(float(message.text))
    await message.reply(text, reply_markup=types.ReplyKeyboardRemove())
    await state.finish()


async def gsm_set_rc(message: types.Message, state: FSMContext):
    try:
        text = models_active.models[message.chat.id].set_rand_coeff(float(message.text))
    except KeyError:
        models_active.check_model_exists(message.chat.id)
        text = models_active.models[message.chat.id].set_rand_coeff(float(message.text))
    await message.reply(text, reply_markup=types.ReplyKeyboardRemove())
    await state.finish()


async def gsm_show_values(message: types.Message, state: FSMContext):
    models_active.check_model_exists(message.chat.id)
    rc = models_active.models[message.chat.id].get_rand_coeff()
    ac = models_active.models[message.chat.id].get_answer_chance()
    text = f'rand_coeff = {rc*100} \nanswer_chance = {ac*100}'
    await message.reply(text, reply_markup=types.ReplyKeyboardRemove())
    await state.finish()


# handlers for bot management settings
async def asm_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, selective=True)
    for option in asm_start_options:
        keyboard.add(option)
    await message.reply('Выбери опцию', reply_markup=keyboard)
    await AdminSettingsMenu.asm_wait_for_option.set()


async def asm_update_bot_chosen(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                         one_time_keyboard=True,
                                         selective=True)
    keyboard.add('*last update log*')
    await message.reply('Запрашиваю обновления...', reply_markup=keyboard)
    await state.finish()
    subprocess.run('/home/timursam00/markov-chat-bot/update', shell=True)


async def asm_show_status_chosen(message: types.Message, state: FSMContext):
    result = subprocess.run('systemctl status markovbot', shell=True, capture_output=True)
    text = result.stdout.decode('utf-8')
    await message.reply(text, reply_markup=types.ReplyKeyboardRemove())
    await state.finish()


async def asm_update_log(message: types.Message, state: FSMContext):
    try:
        with open('/home/timursam00/markov-chat-bot/update.txt', 'r') as file:
            updatelog = file.read()
    except FileNotFoundError:
        updatelog = 'there is no update log'
    await message.answer(text=updatelog, reply_markup=types.ReplyKeyboardRemove())
    await state.finish()


async def asm_anek_settings_chosen(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, selective=True)
    for option in asm_anek_options:
        keyboard.add(option)
    await message.reply('Выбери опцию', reply_markup=keyboard)
    await AdminSettingsMenu.asm_wait_for_anek_option.set()


async def asm_anek_rc_chosen(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, selective=True)
    keyboard.add('/cancel')
    await message.reply('Введите значение в процентах, по умолчанию 0.1', reply_markup=keyboard)
    await AdminSettingsMenu.asm_wait_for_anek_rand_coeff.set()


async def asm_anek_ord_chosen(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, selective=True)
    keyboard.add('/cancel')
    await message.reply('Введите целое значение не менее 10, по умолчанию 12', reply_markup=keyboard)
    await AdminSettingsMenu.asm_wait_for_anek_order.set()


async def asm_anek_set_rc(message: types.Message, state: FSMContext):
    text = models_active.models["ANEKS"].set_rand_coeff(float(message.text))
    await message.reply(text, reply_markup=types.ReplyKeyboardRemove())
    await state.finish()


async def asm_anek_set_ord(message: types.Message, state: FSMContext):
    order = int(message.text)
    if order <= 9:
        text = 'Значение должно быть больше или равно 10'
    else:
        models_active.init_anek_model(order=order,
                                      rand_coeff=0.001,
                                      is_main=True)
        text = 'Успешно'
    await message.reply(text, reply_markup=types.ReplyKeyboardRemove())
    await state.finish()


async def asm_anek_show_values(message: types.Message, state: FSMContext):
    rc = models_active.models["ANEKS"].get_rand_coeff()
    ord = models_active.models["ANEKS"].get_order()
    text = f'rand_coeff = {rc*100} \norder = {ord}'
    await message.reply(text, reply_markup=types.ReplyKeyboardRemove())
    await state.finish()


async def asm_anek_dump(message: types.Message, state: FSMContext):
    text = models_active.dump_to_json("ANEKS")
    await message.reply(text, reply_markup=types.ReplyKeyboardRemove())
    await state.finish()


# registering handlers
def register_handlers_settings(dp: Dispatcher):
    # gsm handlers registering
    dp.register_message_handler(gsm_start,
                                filters.ChatTypeFilter(types.ChatType.CHANNEL),
                                commands="settings",
                                state="*")
    dp.register_message_handler(gsm_start,
                                filters.ChatTypeFilter(types.ChatType.GROUP),
                                commands="settings",
                                state="*")
    dp.register_message_handler(gsm_start,
                                filters.ChatTypeFilter(types.ChatType.SUPERGROUP),
                                commands="settings",
                                state="*")
    dp.register_message_handler(gsm_ac_chosen,
                                filters.Text('answer_chance'),
                                state=GroupSettingsMenu.gsm_wait_for_option)
    dp.register_message_handler(gsm_rc_chosen,
                                filters.Text('rand_coeff'),
                                state=GroupSettingsMenu.gsm_wait_for_option)
    dp.register_message_handler(gsm_set_rc,
                                state=GroupSettingsMenu.gsm_wait_for_rand_coeff)
    dp.register_message_handler(gsm_set_ac,
                                state=GroupSettingsMenu.gsm_wait_for_ans_chance)
    dp.register_message_handler(gsm_show_values,
                                filters.Text('*показать_параметры*'),
                                state=GroupSettingsMenu.gsm_wait_for_option)
    dp.register_message_handler(wrong_opt_chosen,
                                state=GroupSettingsMenu.gsm_wait_for_option)

    # asm handlers registering
    dp.register_message_handler(asm_start,
                                filters.ChatTypeFilter(types.ChatType.PRIVATE),
                                filters.IDFilter(config.admin_ids.admin_id),
                                commands="settings",
                                state="*")
    dp.register_message_handler(asm_update_bot_chosen,
                                filters.Text('*update bot*'),
                                state=AdminSettingsMenu.asm_wait_for_option)
    dp.register_message_handler(asm_show_status_chosen,
                                filters.Text('*show status*'),
                                state=AdminSettingsMenu.asm_wait_for_option)
    dp.register_message_handler(asm_anek_settings_chosen,
                                filters.Text('*aneks settings*'),
                                state=AdminSettingsMenu.asm_wait_for_option)
    dp.register_message_handler(asm_anek_rc_chosen,
                                filters.Text('rand_coeff'),
                                state=AdminSettingsMenu.asm_wait_for_anek_option)
    dp.register_message_handler(asm_anek_ord_chosen,
                                filters.Text('order'),
                                state=AdminSettingsMenu.asm_wait_for_anek_option)
    dp.register_message_handler(asm_anek_set_rc,
                                state=AdminSettingsMenu.asm_wait_for_anek_rand_coeff)
    dp.register_message_handler(asm_anek_set_ord,
                                state=AdminSettingsMenu.asm_wait_for_anek_order)
    dp.register_message_handler(asm_anek_show_values,
                                filters.Text('*показать параметры*'),
                                state=AdminSettingsMenu.asm_wait_for_anek_option)
    dp.register_message_handler(asm_anek_dump,
                                filters.Text('*dump*'),
                                state=AdminSettingsMenu.asm_wait_for_anek_option)
    dp.register_message_handler(asm_update_log,
                                filters.ChatTypeFilter(types.ChatType.PRIVATE),
                                filters.IDFilter(config.admin_ids.admin_id),
                                filters.Text('*update bot*'),
                                state="*")
    dp.register_message_handler(asm_update_log,
                                filters.ChatTypeFilter(types.ChatType.PRIVATE),
                                filters.IDFilter(config.admin_ids.admin_id),
                                filters.Text('*last update log*'),
                                state="*")
    dp.register_message_handler(wrong_opt_chosen,
                                state=AdminSettingsMenu.asm_wait_for_option)
    dp.register_message_handler(wrong_opt_chosen,
                                state=AdminSettingsMenu.asm_wait_for_anek_option)
