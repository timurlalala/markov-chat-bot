import sqlite3

conn = sqlite3.connect('database/messages.db', check_same_thread=False)
cursor = conn.cursor()


def get_cursor():
    return cursor


def insert_or_update(userid: int, message: str):
    statement = "INSERT INTO texts (userid, message) " \
                "VALUES (:userid, :message) "
    cursor.execute(statement, {
        "userid": userid,
        "message": message
    })
    cursor.connection.commit()


def get_random_message(userid: int):
    statement = "SELECT message FROM texts WHERE userid = :userid " \
                "ORDER BY RANDOM()"
    cursor.execute(statement, {
        "userid": userid
    })
    text = cursor.fetchone()
    return text[0]


def _init_db():
    with open(r"C:\Users\timur\PycharmProjects\TelegramBot\database\db.sql", 'r') as file:
        sql = file.read()
    cursor.executescript(sql)
    conn.commit()


def check_db_exists():
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='texts'")
    table_exists = cursor.fetchall()
    if table_exists:
        return
    else:
        _init_db()


check_db_exists()
