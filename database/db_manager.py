import sqlite3
from app.app import config

messages_conn = sqlite3.connect(config.database.messages_path, check_same_thread=False)
messages_cursor = messages_conn.cursor()


def msg_create_table():
    statement = "CREATE TABLE messages ("\
                "id INTEGER not null primary key, " \
                "chatid INTEGER not null," \
                "userid INTEGER not null, " \
                "message TEXT not null, " \
                "time REAL not null, " \
                "last_ans TEXT" \
                ");"
    messages_cursor.execute(statement)
    messages_conn.commit()


def msg_check_table_exist():
    statement = "SELECT name FROM sqlite_master " \
                "WHERE type='table'" \
                "AND name='messages';"
    messages_cursor.execute(statement)
    table_exists = messages_cursor.fetchall()
    if table_exists:
        pass
    else:
        msg_create_table()


def msg_insert_or_update(chatid: int, userid: int, message: str, timestamp: float, last_ans: str):
    """Inserts or update text message in database"""
    statement = "INSERT INTO messages (chatid, userid, message, time, last_ans) " \
                "VALUES (:chatid, :userid, :message, :timestamp, :last_ans);"
    messages_cursor.execute(statement, {
        "chatid": chatid,
        "userid": userid,
        "message": message,
        "timestamp": timestamp,
        "last_ans": last_ans
    })
    messages_conn.commit()


def msg_get_cursor():
    return messages_cursor


aneks_conn = sqlite3.connect(config.database.anecdotes_path, check_same_thread=False)
aneks_cursor = aneks_conn.cursor()


def anek_get_cursor():
    return aneks_cursor


msg_check_table_exist()
