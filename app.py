import os
import sys
import sqlite3
from datetime import date
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
        row = cur.execute("SELECT * FROM users WHERE username = ?;", (username,)).fetchone()

        if row:
            error_msg = "Username already exists, please a different username"
            conn.close()
            return render_template("registration.html", error_msg=error_msg)
        else:
            # insert user into database
            hash = generate_password_hash(password, method='sha256')
            try:
                cur.execute("INSERT INTO users (first_name, last_name, username, hash, email) VALUES (?, ?, ?, ?, ?);", (fname, lname, username, hash, email))
                conn.commit()
            except:
                error_msg = "Error inserting into database"
                conn.close()
                return render_template("registration.html", error_msg=error_msg)
            conn.close()
            return redirect("login")
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
        
        # print(f"======= {row['username']} =======", file=sys.stderr)
        
        if not row or not check_password_hash(row["hash"], password):
            error_msg = "Invalid username or password!"
            conn.close()
            return render_template("login.html", error_msg=error_msg)
        
        # remember user that is logged in
        session["user_id"] = row["id"]
        try:
            cur.execute("UPDATE users SET last_login_date = ? WHERE id = ?", (date.today(), session["user_id"]))
            conn.commit()
        except:
            error_msg = "Couldn't update login time"
            conn.close()
            return render_template("login.html", error_msg=error_msg)
        conn.close()
        return redirect("/")
    return render_template("login.html")


@app.route("/logout")
def logout():
    # forget user id
    session.clear()

    # redirect to login
    return redirect("login")


@app.route("/profile", methods=["GET", "POST"])
def profile():
    # if "GET" display all the information the DB has on the user
    if request.method == "GET":
        # connect DB
        conn = get_database_connection()
        cur = conn.cursor()

        # get user info
        user_data = cur.execute("SELECT first_name, last_name, username, email FROM users WHERE id = ?;", (session["user_id"],)).fetchall()
        conn.close()
        #print(f"======= {user_data[0]['first_name']} =======", file=sys.stderr)
        return render_template("profile.html", user_data=user_data)
    # if "POST" update user information
    if request.method == "POST":
        fname = request.form.get("fname")
        lname = request.form.get("lname")
        username = request.form.get("username")
        email = request.form.get("email")

        conn = get_database_connection()
        cur = conn.cursor()
        user_data = cur.execute("SELECT first_name, last_name, username, email FROM users WHERE id = ?;", (session["user_id"],)).fetchall()
        # if all the fields are empty
        if not fname and not lname and not username and not email:
            error_msg = "If you want to change data, you have to input some information"
            return render_template("profile.html", user_data=user_data, error_msg=error_msg)
        
        # check which field to update
        if fname:
            cur.execute("UPDATE users SET first_name = ? WHERE id = ?", (fname, session["user_id"]))
            conn.commit()
            return redirect("profile")
        if lname:
            cur.execute("UPDATE users SET last_name = ? WHERE id = ?", (lname, session["user_id"]))
            conn.commit()
            return redirect("profile")
        if username:
            row = cur.execute("SELECT username FROM users WHERE username = ?", (username,)).fetchone()
            if row:
                return render_template("profile.html", user_data=user_data, error_msg="Username already exists!")
            cur.execute("UPDATE users SET username = ? WHERE id = ?", (username, session["user_id"]))
            conn.commit()
            return redirect("profile")
        if email:
            row = cur.execute("SELECT username FROM users WHERE username = ?", (username,)).fetchone()
            if row:
                return render_template("profile.html", user_data=user_data, error_msg="This e-mail is already registered!")
            cur.execute("UPDATE users SET email = ? WHERE id = ?", (email, session["user_id"]))
            conn.commit()
            return redirect("profile")
        
        return render_template("profile.html")
    

@app.route("/insert_address", methods=["GET", "POST"])
def insert_address():
    # GET -> display form 

    # POST -> insert into DB
    return render_template("/")

@app.route("/products")
def products():
    # connect DB
    conn = get_database_connection()
    cur = conn.cursor()

    rows = cur.execute("SELECT * FROM products;").fetchall()
    return render_template("products.html", rows=rows)