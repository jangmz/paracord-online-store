import os
import sqlite3
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
#app.secret_key = "1ooK4tM3mY5r1EnD_L00L_Dud3"
Session(app)

@app.after_request
def after_request(response):
    # Ensure responses aren't cached
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# connect database
def get_database_connection():
    conn = sqlite3.connect("paracord.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/index")
def index():
    return render_template("index.html")


@app.route("/registration", methods=["GET", "POST"])
def registration():
    if request.method == "POST":
        # save all input fields
        fname = request.form.get("fname")
        lname = request.form.get("lname")
        email = request.form.get("email").lower()
        username = request.form.get("username").lower()
        password = request.form.get("password")

        # check that fields are not empty
        if not fname or not lname or not email or not username or not password:
            error_msg = "Please fill out all fields"
            return render_template("registration.html", error_msg=error_msg)

        # create cursor from DB connection
        conn = get_database_connection()
        cur = conn.cursor()

        # check if username or email already exist
        row = cur.execute("SELECT username FROM users WHERE username = ?;", (username,)).fetchone()
        row2 = cur.execute("SELECT email FROM users WHERE email = ?;", (email,)).fetchone()
        if row or row2:
            error_msg = "Username/e-mail already exists, please a different username/e-mail"
            return render_template("registration.html", error_msg=error_msg)
        else:
            # insert user into database
            hash = generate_password_hash(password, method='sha256')
            try:
                cur.execute("INSERT INTO users (first_name, last_name, username, hash, email) VALUES (?, ?, ?, ?, ?);", (fname, lname, username, hash, email))
                conn.commit()
            except:
                error_msg = "Error inserting into database"
                return render_template("registration.html", error_msg=error_msg)
            return redirect("/")
    return render_template("registration.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # check if fields are empty
        if not username or not password:
            error_msg = "Please input username or/and password."
            return render_template("login.html", error_msg=error_msg)
        
        # DB connection
        conn = get_database_connection()
        cur = conn.cursor()

        # query username
        row = cur.execute("SELECT * FROM users WHERE username = ?",(username,)).fetchone()
        if not row or not check_password_hash(rows[0]["hash"], password):
            error_msg = "Invalid username or password!"
            return render_template("login.html", error_msg=error_msg)
        # continue here *****************************************
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("login")