import sqlite3
import re
import sys

def parse_scenario_file(file_path):
    with open(file_path, 'r') as file:
        text = file.read()

    scenario = {}
    locations = []

    # Получение данных о сценарии
    scenario_match = re.search(r'\[Сценарий: (.*?)\]', text)
    if scenario_match:
        scenario['name'] = scenario_match.group(1)

    desc_match = re.search(r'\[START_DESCRIPTION\](.*?)\[END_DESCRIPTION\]', text, re.DOTALL)
    if desc_match:
        scenario['description'] = '\n'.join([line.strip() for line in desc_match.group(1).split('\n')])  # Удаление лишних пробелов

    # Разделение текста по локациям
    location_texts = re.split(r'- Название локации', text)
    for loc_text in location_texts[1:]:  # Пропускаем первую часть текста (до первой локации)
        loc_lines = loc_text.split('\n')

        current_location = {'name': loc_lines[0].strip()}
        desc_match = re.search(r'\[START\](.*?)\[END\]', loc_text, re.DOTALL)
        if desc_match:
            current_location['description'] = '\n'.join([line[2:] for line in desc_match.group(1).split('\n')])  # Удаление лишних пробелов

        photo_match = re.search(r'Фото: (.*?)\n', loc_text)
        if photo_match:
            current_location['photo'] = photo_match.group(1)

        char_matches = re.finditer(r'- Имя персонажа (.*?)\[START\](.*?)\[END\]', loc_text, re.DOTALL)
        characters = []
        for char_match in char_matches:
            char_desc = '\n'.join([line[4:] for line in char_match.group(2).split('\n')])  # Удаление лишних пробелов
            characters.append({'name': char_match.group(1).strip(), 'description': char_desc.strip()})

        current_location['characters'] = characters
        locations.append(current_location)

    scenario['locations'] = locations
    return scenario


def insert_scenario_to_database(scenario):
    conn = sqlite3.connect('game.db')  # Подключение к вашей базе данных SQLite
    print(conn.total_changes)
    cursor = conn.cursor()

    # Вставка данных о сценарии
    cursor.execute("INSERT INTO scenarios (name, history) VALUES (?, ?)", (scenario['name'], scenario['description']))
    scenario_id = cursor.lastrowid

    # Вставка данных о локациях
    for location in scenario['locations']:
        cursor.execute("INSERT INTO locations (scenario_id, name, description, photo) VALUES (?, ?, ?, ?)",
                       (scenario_id, location['name'], location['description'], location.get('photo', '')))
        location_id = cursor.lastrowid

        # Вставка данных о персонажах
        for character in location.get('characters', []):
            cursor.execute("INSERT INTO characters (location_id, name, description, photo) VALUES (?, ?, ?, ?)",
                           (location_id, character['name'], character['description'], character.get('photo', '')))

    conn.commit()
    conn.close()

# Использование парсера и вставка данных в базу
file_path = sys.argv[1]
parsed_scenario = parse_scenario_file(file_path)
insert_scenario_to_database(parsed_scenario)

#6017972063:AAHXvzg9U8Rjy821Z8NiQWRZDfuxiXT-Nyo