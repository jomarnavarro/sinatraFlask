import os
import sqlite3

from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd, is_int, meets_complexity
import db_helpers

# Configure application
app = Flask(__name__)


# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Error - You must provide a username")
            return render_template("login.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Error - You must provide a username")
            return render_template("login.html")

        rows = db_helpers.query_username(request.form.get('username'))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("Error - invalid username and/or password")
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # TODO - make sure one sets the session['user_type']
        user_type = db_helpers.get_user_type(session['user_id'])
        session['user_type'] = user_type
        # Redirect user to home page
        flash(f"Welcome {request.form.get('username')}")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    user_id = session["user_id"]

    user_name = db_helpers.get_username_by_id(user_id)[0]['username']
    print(user_name)
    

    # Forget any user_id
    session.clear()
    flash(f"Goodbye {user_name}")
    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register regular user"""
    if request.method == "GET":
        return render_template("register.html")
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        repeat_password = request.form.get('repeat_password')
        if not username:
            flash("Error - You must enter a username")
            return render_template("register.html")
        if not password or not repeat_password:
            flash("Error - You must enter a password that matches")
            return render_template("register.html")
        if password != repeat_password:
            flash('Passwords do not match.')
            return render_template("register.html")
        # if not meets_complexity(password):
        #     return apology(
        #         'Password must: \n\t-be 8+ characters long.\n\t-contain uppercase and lowercase letters\n\t-a number '
        #         'and a symbol\n\n',
        #         403)

        rows = db_helpers.query_username(username)

        if len(rows) != 0:
            flash(f"User '{username}' is already taken")
            return render_template("register.html")

        db_helpers.insert_user(username, generate_password_hash(password), 'user')
        flash(f"{username} was succesfully registered.")
        return render_template("login.html")


@app.route("/about")
def about():
    return render_template('about.html')


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == 'GET':
        return render_template('contact.html')
    else:
        # do the magic of processing the contact form and add it to the database.
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        if not email:
            flash("You need to enter an email")
            return render_template("contact.html")
        if not message:
            flash("You need to enter a message")
            return render_template("contact.html")

        db_helpers.insert_message(name, email, message)
        flash("Message received.")
        return redirect('/')


@app.route('/songs')
def list_songs():
    # get all songs from the database
    rows = db_helpers.fetch_songs()
    return render_template('songs.html', songs=rows)


@app.route('/songs/<int:song_number>')
def list_song_number(song_number):
    # get all songs from the database
    row = db_helpers.fetch_song_info(song_number)
    if not row:
        flash(f"Song {song_number} does not exist.")
        return render_template("songs.html")
    
    return render_template('song.html', song_info=row)


@app.route("/like/<int:song_number>")
def like_song(song_number):
    # update number of likes
    db_helpers.update_number_likes(song_number)
    flash("Thank you for your like")
    return redirect(f"/songs/{song_number}")


@app.route("/songs/new", methods=["GET", "POST"])
def create_song():
    if request.method == "GET":
        return render_template("song_form.html")
    else:
        # fetch form data
        messages = []
        artist = request.form.get("artist")
        country = request.form.get("country")
        title = request.form.get("title")
        duration = request.form.get("duration")
        lyrics = request.form.get("lyrics")
        
        if not artist:
            messages.append("Your song has no artist name")
        if not country:
            country = ''
            messages.append("Your song has no country for artist")
        if not title:
            messages.append("Your song needs a title")
        if not duration:
            duration = 0
            messages.append("Your song has no duration time")
        if not lyrics:
            lyrics = ''
            messages.append("Your song has no lyrics")

        if not artist and not title and not country:
            for msg in messages:
                flash(msg)
            return render_template("song_form.html")
        print(f"before getting artist_id, title is {title}")
        # get the artist id, whether it exists or is inserted on the spot.
        artist_id = db_helpers.get_artist_id(artist, country)
        print(f"after getting artist_id, title is {title}")
        print(artist_id)
        # get the song_id, whether it exists already or is added
        
        song_id, existed = db_helpers.get_song_id(title, duration, artist_id, lyrics)
        print(song_id)
        if existed:
            flash(f"Song {title} already existed in the DB.  Pls edit it.")
        # insert song into database
        # get song id
        # redirect user to /song/id
        return redirect(f"/songs/{song_id}")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
