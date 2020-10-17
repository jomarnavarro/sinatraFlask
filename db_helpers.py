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


def get_username_by_id(uid):
    """Get the username by the id"""
    username_select = "SELECT username FROM users WHERE id=?"
    test = (uid,)
    c.execute(username_select, test)
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


def get_artist_id(artist, nationality):
    """Gets the artist id, whether it exists or has to insert it"""
    artist_id_select = "SELECT id FROM artist WHERE name = ? and nationality = ?"
    test = (artist, nationality)
    c.execute(artist_id_select, test)
    row = c.fetchone()
    if row is None:
        # insert the motherfucker
        # TODO get the image URL
        # TODO if no image is found, img_url = '', 
        # TODO send a message to the user.
        img_url = ''
        artist_insert = "INSERT INTO artist (name, nationality, img_url) VALUES (?, ?, ?)"
        test2 = (artist, nationality, img_url)
        c.execute(artist_insert, test2)
        conn.commit()
        
        # retry the select,
        c.execute(artist_id_select, test)
        row = c.fetchone()
    return row['id']

def get_song_id(title, duration, artist_id, lyrics):
    song_id_select = "SELECT id FROM songs WHERE title = ? and artist_id = ?"
    test = (title, artist_id)
    c.execute(song_id_select, test)
    row = c.fetchone()
    if not row:
        # insert the motherfucker
        print(title)
        song_insert = "INSERT INTO songs (title, duration, artist_id, lyrics, num_likes) VALUES (?, ?, ?, ?, ?)"
        test2 = (title, duration, artist_id, lyrics, 0)
        c.execute(song_insert, test2)
        conn.commit()
         
        #retry the select
        c.execute(song_id_select, test)
        row = c.fetchone()
        return row['id'], False
    else:
        return row['id'], True


def update_song_info(song_number, artist_id, duration, lyrics):
    update_song = "UPDATE songs SET artist_id = ?, duration = ?, lyrics = ? WHERE id = ?"
    test = (artist_id, duration, lyrics, song_number)
    c.execute(update_song, test)
    conn.commit()


def delete_song(song_number):
    delete_song = "DELETE FROM songs WHERE id = ?"
    test = (song_number, )
    c.execute(delete_song, test)
    conn.commit()