import sqlite3
import re
import sys

def parse_questions_file(file_path):
    with open(file_path, 'r') as file:
        text = file.read()

    questions = []
    current_category_id = None

    # Разделение текста по категориям
    category_texts = re.split(r'\[Категория: (.*?)\]', text)
    for i in range(1, len(category_texts), 2):  # Начинаем с 1, так как 0-й элемент - это текст до первой категории
        category_name = category_texts[i]
        category_text = category_texts[i + 1]

        # Разбиваем текст категории по строкам
        category_lines = category_text.strip().split('\n')

        for line in category_lines:
            parts = line.strip().split('. ', 1)
            if len(parts) == 2:
                questions.append({'category_name': category_name, 'text': parts[1]})

    return questions

def insert_questions_to_database(questions, scenario_id):
    conn = sqlite3.connect('game.db')  # Подключение к вашей базе данных SQLite
    cursor = conn.cursor()

    for question in questions:
        # Проверяем существование категории
        cursor.execute("SELECT id FROM question_categories WHERE scenario_id = ? AND category_name = ?",
                       (scenario_id, question['category_name']))
        category_row = cursor.fetchone()

        if category_row:
            category_id = category_row[0]
        else:
            # Если категории нет, добавляем ее
            cursor.execute("INSERT INTO question_categories (scenario_id, category_name) VALUES (?, ?)",
                           (scenario_id, question['category_name']))
            category_id = cursor.lastrowid

        # Вставляем вопрос
        cursor.execute("INSERT INTO questions (scenario_id, category_id, question_text) VALUES (?, ?, ?)",
                       (scenario_id, category_id, question['text']))

    conn.commit()
    conn.close()

# Использование парсера и вставка данных в базу
file_path = sys.argv[1]
parsed_questions = parse_questions_file(file_path)
scenario_id = sys.argv[2]
insert_questions_to_database(parsed_questions, scenario_id)  # Замените scenario_id на актуальное значение
