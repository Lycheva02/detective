import telebot
from telebot import types
import sqlite3

bot = telebot.TeleBot("TOKEN")

# Здесь добавляем состояние для пользователя
user_states = {}
cur_loc = ''

def get_locations(scenario_id):
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM locations WHERE scenario_id = ?", (scenario_id,))
    locations = cursor.fetchall()
    conn.close()
    return [location[0] for location in locations]

def get_characters(location_name, scenario_id):
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM characters WHERE location_id = (SELECT id FROM locations WHERE name = ? AND scenario_id = ?)", (location_name, scenario_id))
    characters = cursor.fetchall()
    conn.close()
    return [character[0] for character in characters]

@bot.message_handler(commands=['start'])
def start(message):
    global user_states
    keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    btn1 = types.KeyboardButton("Сценарий 1")
    btn2 = types.KeyboardButton('Сценарий 2')
    keyboard.add(btn1, btn2)
    bot.send_message(message.chat.id, "Выберите сценарий:", reply_markup=keyboard)
    # Начальное состояние пользователя
    user_states[message.chat.id] = {'state': 'scenario_choice'}
    bot.register_next_step_handler(message, process_scenario_choice)

def process_scenario_choice(message):
    global user_states
    if message.text.startswith('Сценарий'):
        scenario_id = int(message.text.split()[1])
        locations = get_locations(scenario_id)
        reply_markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        buttons = [types.KeyboardButton(location) for location in locations]
        reply_markup.add(*buttons, types.KeyboardButton('Сменить локацию'))
        bot.send_message(message.chat.id, f"Выберите локацию:", reply_markup=reply_markup)
        # Обновляем состояние пользователя
        user_states[message.chat.id] = {'state': 'location_choice', 'scenario_id': scenario_id}
        bot.register_next_step_handler(message, process_location_choice)

def process_location_choice(message):
    global cur_loc, user_states
    scenario_id = user_states[message.chat.id]['scenario_id']
    if message.text == 'Сменить локацию':
        # Возвращаем пользователя к выбору локации
        locations = get_locations(scenario_id)
        reply_markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        buttons = [types.KeyboardButton(location) for location in locations]
        reply_markup.add(*buttons)
        bot.send_message(message.chat.id, f"Выберите локацию:", reply_markup=reply_markup)
        bot.register_next_step_handler(message, process_location_choice)
        return
    location_name = message.text
    cur_loc = location_name
    bot.send_message(message.chat.id, f"Вы выбрали локацию: {location_name}")
    characters = get_characters(location_name, scenario_id)
    reply_markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    buttons = [types.KeyboardButton(character) for character in characters]
    reply_markup.add(*buttons, types.KeyboardButton('Сменить локацию'))
    bot.send_message(message.chat.id, "Выберите персонажа:", reply_markup=reply_markup)
    # Обновляем состояние пользователя
    user_states[message.chat.id]['state'] = 'character_choice'
    bot.register_next_step_handler(message, process_character_choice)

def process_character_choice(message):
    global cur_loc, user_states
    scenario_id = user_states[message.chat.id]['scenario_id']
    if message.text == 'Сменить персонажа':
        # Возвращаем пользователя к выбору персонажа
        location_name = cur_loc
        characters = get_characters(location_name, scenario_id)
        reply_markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        buttons = [types.KeyboardButton(character) for character in characters]
        reply_markup.add(*buttons, types.KeyboardButton('Сменить локацию'))
        bot.send_message(message.chat.id, "Выберите персонажа:", reply_markup=reply_markup)
        bot.register_next_step_handler(message, process_character_choice)
        return
    elif message.text == 'Сменить локацию':
        locations = get_locations(scenario_id)
        reply_markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        buttons = [types.KeyboardButton(location) for location in locations]
        reply_markup.add(*buttons)
        bot.send_message(message.chat.id, f"Выберите локацию:", reply_markup=reply_markup)
        bot.register_next_step_handler(message, process_location_choice)
        return
    character_name = message.text
    reply_markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    reply_markup.add(types.KeyboardButton('Сменить персонажа'), types.KeyboardButton('Сменить локацию'))
    bot.send_message(message.chat.id, f"Вы выбрали персонажа: {character_name}", reply_markup=reply_markup)
    bot.register_next_step_handler(message, process_character_choice)

bot.polling()
