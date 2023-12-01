import telebot
from telebot import types
import sqlite3

bot = telebot.TeleBot("TOKEN")

# Здесь добавляем состояние для пользователя
user_states = {}
cur_loc = ''

def get_scenarios():
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM scenarios")
    scenario_names = [row[0] for row in cursor.fetchall()]
    conn.close()
    return scenario_names

def get_scenario_id(scenario_name):
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM scenarios WHERE name = ?", (scenario_name,))
    result = cursor.fetchone()
    conn.close()
    return result[0]

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

def get_categories(scenario_id):
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    cursor.execute("SELECT category_name FROM question_categories WHERE scenario_id = ?", (scenario_id,))
    categories = cursor.fetchall()
    conn.close()
    return [category[0] for category in categories]

def get_questions(category_name, scenario_id):
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    # Получаем id категории
    cursor.execute("SELECT id FROM question_categories WHERE scenario_id = ? AND category_name = ?", (scenario_id, category_name))
    category_row = cursor.fetchone()
    category_id = category_row[0]
    cursor.execute("SELECT question_text FROM questions WHERE scenario_id = ? AND category_id = ?", (scenario_id, category_id))
    questions = cursor.fetchall()
    conn.close()
    return [question[0] for question in questions]

@bot.message_handler(commands=['start'])
def start(message):
    global user_states
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    scenarios = get_scenarios()
    buttons = [types.KeyboardButton(s) for s in scenarios]
    keyboard.add(*buttons)
    bot.send_message(message.chat.id, "*Выберите сценарий:*", reply_markup=keyboard, parse_mode="MarkdownV2")
    user_states[message.chat.id] = {'state': 'scenario_choice'}
    bot.register_next_step_handler(message, process_scenario_choice)

def process_scenario_choice(message):
    global user_states
    scenario_id = get_scenario_id(message.text)
    locations = get_locations(scenario_id)
    reply_markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    buttons = [types.KeyboardButton(location) for location in locations]
    reply_markup.add(*buttons)
    bot.send_message(message.chat.id, f"*Выберите локацию:*", reply_markup=reply_markup, parse_mode="MarkdownV2")
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
        bot.send_message(message.chat.id, f"*Выберите локацию:*", reply_markup=reply_markup, parse_mode="MarkdownV2")
        bot.register_next_step_handler(message, process_location_choice)
        return
    location_name = message.text
    cur_loc = location_name
    characters = get_characters(location_name, scenario_id)
    reply_markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    buttons = [types.KeyboardButton(character) for character in characters]
    reply_markup.add(*buttons, types.KeyboardButton('Сменить локацию'))
    bot.send_message(message.chat.id, "*Выберите персонажа:*", reply_markup=reply_markup, parse_mode="MarkdownV2")
    # Обновляем состояние пользователя
    user_states[message.chat.id]['state'] = 'character_choice'
    bot.register_next_step_handler(message, process_character_choice)

def process_character_choice(message):
    global cur_loc, user_states
    scenario_id = user_states[message.chat.id]['scenario_id']
    if message.text == 'Сменить локацию':
        locations = get_locations(scenario_id)
        reply_markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        buttons = [types.KeyboardButton(location) for location in locations]
        reply_markup.add(*buttons)
        bot.send_message(message.chat.id, f"*Выберите локацию:*", reply_markup=reply_markup, parse_mode="MarkdownV2")
        bot.register_next_step_handler(message, process_location_choice)
        return
    character_name = message.text
    categories = get_categories(scenario_id)
    buttons = [types.KeyboardButton(category) for category in categories]
    reply_markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    reply_markup.add(*buttons, types.KeyboardButton('Сменить персонажа'), types.KeyboardButton('Сменить локацию'))
    bot.send_message(message.chat.id, f"*Вы выбрали персонажа: {character_name}*", reply_markup=reply_markup, parse_mode="MarkdownV2")
    bot.register_next_step_handler(message, process_category_choice)

def process_category_choice(message):
    global cur_loc, user_states
    scenario_id = user_states[message.chat.id]['scenario_id']
    if message.text == 'Сменить персонажа':
        # Возвращаем пользователя к выбору персонажа
        location_name = cur_loc
        characters = get_characters(location_name, scenario_id)
        reply_markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        buttons = [types.KeyboardButton(character) for character in characters]
        reply_markup.add(*buttons, types.KeyboardButton('Сменить локацию'))
        bot.send_message(message.chat.id, "*Выберите персонажа:*", reply_markup=reply_markup, parse_mode="MarkdownV2")
        bot.register_next_step_handler(message, process_character_choice)
        return
    elif message.text == 'Сменить локацию':
        locations = get_locations(scenario_id)
        reply_markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        buttons = [types.KeyboardButton(location) for location in locations]
        reply_markup.add(*buttons)
        bot.send_message(message.chat.id, f"*Выберите локацию:*", reply_markup=reply_markup, parse_mode="MarkdownV2")
        bot.register_next_step_handler(message, process_location_choice)
        return
    category_name = message.text
    reply_markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    questions = get_questions(category_name, scenario_id)
    buttons = [types.KeyboardButton(question) for question in questions]
    reply_markup.add(*buttons, types.KeyboardButton('Сменить персонажа'), types.KeyboardButton('Сменить локацию'))
    bot.send_message(message.chat.id, f"*Вы выбрали категорию: {category_name}*", reply_markup=reply_markup, parse_mode="MarkdownV2")
    bot.register_next_step_handler(message, process_question_choice)

def process_question_choice(message):
    pass

bot.polling()
