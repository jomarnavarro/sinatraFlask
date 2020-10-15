import sqlite3

conn = sqlite3.connect('sinatra.db', check_same_thread=False)
conn.row_factory = sqlite3.Row
c = conn.cursor()


def query_username(username):
    """ Query database for username """
    user_select = "SELECT * FROM users WHERE username = ?"
    test = (username,)
    c.execute(user_select, test)
    return c.fetchall()


def insert_user(username, password, user_type):
    """Insert User into the database"""
    user_insert_select = "INSERT INTO users (username, hash, user_type) VALUES (?, ?, ?)"
    test = (username, password, user_type)
    c.execute(user_insert_select, test)
    conn.commit()


def get_user_type(user_id):
    user_type_select = "SELECT user_type FROM users WHERE id = ?"
    test = (user_id,)
    c.execute(user_type_select, test)
    rows = c.fetchone()
    return rows['user_type']


def insert_message(name, email, message):
    if not name:
        name = ''
    message_insert = "INSERT INTO messages (name, email, message, read) VALUES (?, ?, ?, ?)"
    test = (name, email, message, 0)
    c.execute(message_insert, test)
    conn.commit()
