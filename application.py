import os
import sqlite3

from flask import Flask, flash, jsonify, redirect, render_template, request, session
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
@login_required
def index():
    return apology("TODO", 404)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        rows = db_helpers.query_username(request.form.get('username'))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # TODO - make sure one sets the session['user_type']
        user_type = db_helpers.get_user_type(session['user_id'])
        session['user_type'] = user_type
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

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
            return apology('You did not enter a username.', 403)
        if not password or not repeat_password:
            return apology('You did not enter a password.', 403)
        if password != repeat_password:
            return apology('Passwords do not match.', 403)
        # if not meets_complexity(password):
        #     return apology(
        #         'Password must: \n\t-be 8+ characters long.\n\t-contain uppercase and lowercase letters\n\t-a number '
        #         'and a symbol\n\n',
        #         403)

        rows = db_helpers.query_username(username)

        if len(rows) != 0:
            return apology(f"{username} is already taken", 403)

        db_helpers.insert_user(username, generate_password_hash(password), 'user')

        return redirect("/login")


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
            return apology('You need to enter an email', 402)
        if not message:
            return apology('You need to enter a message', 402)

        db_helpers.insert_message(name, email, message)

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
        return apology(f"Song {song_number} does not exist", 404)
    
    return render_template('song.html', song_info=row)


@app.route("/like/<int:song_number>")
def like_song(song_number):
    # update number of likes
    db_helpers.update_number_likes(song_number)
    return redirect(f"/songs/{song_number}")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
