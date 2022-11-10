import json
import sqlite3


def insert_valid_words(cursor: sqlite3.Cursor) -> int:

    with open("./share/valid.json") as f:
        words = json.load(f)

    for word in words:
        cursor.execute(
            "INSERT INTO valid_words (word, correct_word) VALUES (?, 0)", (word,)
        )

    with open("./share/correct.json") as f:
        correct_words = json.load(f)

    for word in correct_words:
        cursor.execute(
            "INSERT INTO valid_words (word, correct_word) VALUES (?, 1)", (word,)
        )

    return len(words) + len(correct_words)


if __name__ == "__main__":
    connection = sqlite3.connect("./var/wordle.db")
    cursor = connection.cursor()

    count = insert_valid_words(cursor)
    connection.commit()
    print(f"Successfully inserted {'{:,}'.format(count)} words")
