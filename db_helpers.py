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


def fetch_songs():
    songs_join = "SELECT s.id, s.title, a.name, a.img_url FROM songs s JOIN artist a ON s.artist_id = a.id LIMIT 10;"
    test = ()
    c.execute(songs_join, test)
    return c.fetchall()

def fetch_song_info(n):
    song_join = "SELECT s.id, s.title, s.duration, s.lyrics, s.num_likes, a.name, a.nationality, a.img_url FROM songs s JOIN artist a ON s.artist_id = a.id WHERE s.id = ?"
    test = (n, )
    c.execute(song_join, test)
    return c.fetchone()


def update_number_likes(song_number):
    # get the number of likes
    num_likes_select = "SELECT num_likes FROM songs WHERE id=?"
    test = (song_number, )
    c.execute(num_likes_select, test)
    row = c.fetchone()
    num_likes = row['num_likes']
    # update the number of likes
    update_likes = "UPDATE songs SET num_likes = ? WHERE id = ?"
    test = (num_likes + 1, song_number)
    c.execute(update_likes, test)
    conn.commit()
