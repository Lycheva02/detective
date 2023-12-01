import re
import sqlite3
import sys

def parse_answers_file(file_path, scenario_id):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()

    questions = re.findall(r'\[(\d+)\. (.*?)\]\n(.*?)(?=\[\d+\.|\Z)', text, re.DOTALL)

    answers_data = []
    for _, question, question_text in questions:
        locations = re.findall(r'\[Локация (.*?)\] : \[Персонаж (.*?)\]\n\[START\](.*?)\[END\]', question_text, re.DOTALL)
        for location, character, answer_text in locations:
            answers_data.append({
                'question': question.strip(),
                'scenario_id': scenario_id,
                'location': location.strip(),
                'character': character.strip(),
                'answer': answer_text.strip()
            })

    return answers_data

def insert_answers_to_database(answers_data, scenario_id):
    conn = sqlite3.connect('game.db')  # Подключение к вашей базе данных SQLite
    cursor = conn.cursor()

    for answer in answers_data:
        # Получаем id вопроса
        cursor.execute("SELECT id FROM questions WHERE question_text = ? AND scenario_id = ?", (answer['question'], scenario_id))
        question_id = cursor.fetchone()[0]

        # Получаем id локации
        cursor.execute("SELECT id FROM locations WHERE name = ? AND scenario_id = ?", (answer['location'], scenario_id))
        location_id = cursor.fetchone()[0]  # Получаем первый элемент кортежа

        # Получаем id персонажа
        cursor.execute("SELECT id FROM characters WHERE name = ? AND location_id = ?", (answer['character'], location_id))
        character_id = cursor.fetchone()[0]  # Получаем первый элемент кортежа

        # Вставляем ответ в таблицу answers
        cursor.execute("INSERT INTO answers (character_id, question_id, scenario_id, location_id, answer) VALUES (?, ?, ?, ?, ?)",
                       (character_id, question_id, answer['scenario_id'], location_id, answer['answer']))

    conn.commit()
    conn.close()

file_path = sys.argv[1]
scenario_id = sys.argv[2]
answers_data = parse_answers_file(file_path, scenario_id)
insert_answers_to_database(answers_data, scenario_id)
