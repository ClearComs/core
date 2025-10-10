import csv
import random

def pick_random_questions (csv_file, num_questions=10):
    # Read the CSV file
    try:
        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            row = list(reader)
    except UnicodeDecodeError:
        # Try with different encodings if UTF-8 fails
        try:
            with open(csv_file, newline='', encoding='latin-1') as file:
                reader = csv.DictReader(file)
                row = list(reader)
        except UnicodeDecodeError:
            with open(csv_file, newline='', encoding='cp1252') as file:
                reader = csv.DictReader(file)
                row = list(reader)

    # Randomize what questions are picked, and use num_questions for how many questions
    selected_rows = random.sample(row, num_questions)

    # Gets questions into dictionary
    quiz_questions = []
    for row in selected_rows:
        question_dict = {
            'Q': row['Question'],
            'Opt_1': row['Option 1'],
            'Opt_2': row['Option 2'],
            'Opt_3': row['Option 3'],
            'Opt_4': row['Option 4'],
            'A': row['Correct Answer']
        }
        quiz_questions.append(question_dict)

    return quiz_questions
