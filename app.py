import os
import sys
import sqlite3
import pprint
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
    conn.close()
    return render_template("products.html", rows=rows)


@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    # gather data from the product
    data = request.get_json()
    productID = data["productId"]
    #productName = data["productName"]
    #productPrice = data["productPrice"]
    #productQuantity = data["productQuantity"]

    # add to DB
    conn = get_database_connection()
    cur = conn.cursor()
    
    # check if product is already in cart
    row = cur.execute("SELECT * FROM cart WHERE product_id = ? AND user_id = ?", (productID, session["user_id"])).fetchone()
    if row:
        # if yes -> update the cart
        cur.execute("UPDATE cart SET quantity = ? WHERE product_id = ? AND user_id = ?", (row["quantity"] + 1, productID, session['user_id']))
    else:
        # if not -> create an entry
        cur.execute("""INSERT INTO cart(user_id, product_id, quantity, created_at, is_ordered)
            VALUES (?, ?, ?, ?, ?);""", (session["user_id"], productID, 1, date.today(), 0))
    conn.commit()
    conn.close()
    #print(f"======= VALUE OF ALERT: TRUE =======", file=sys.stderr)
    return render_template("products.html")


@app.route("/cart")
def cart():
    # display cart from DB
    conn = get_database_connection()
    cur = conn.cursor()
    cart_data = cur.execute("""SELECT products.id AS id, products.name, cart.quantity AS quantity, products.price
        FROM products
        JOIN cart ON products.id = cart.product_id
        JOIN users ON cart.user_id = users.id
        WHERE users.id = ?""", (session['user_id'],)).fetchall()
    
    # get the total amount of products in the cart
    rows = cur.execute("""SELECT products.price, cart.quantity
        FROM products
        JOIN cart ON products.id = cart.product_id
        JOIN users ON cart.user_id = users.id
        WHERE users.id = ?""", (session['user_id'],)).fetchall()
    total = 0
    for row in rows:
        total += row['price'] * row['quantity']
    
    # get cash amount available
    row = cur.execute("SELECT cash FROM users WHERE id = ?;", (session["user_id"], )).fetchone()
    
    #cart data and total amount sent to the page
    conn.close()
    return render_template("cart.html", cart_data=cart_data, total_amount=total, cash=row["cash"])


@app.route("/remove_product", methods=["POST"])
def remove_product():
    if request.method == "POST":
        product_id = request.form.get("product_id")
        
        # remove from DB cart
        conn = get_database_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM cart WHERE product_id = ?;", (product_id,))
        conn.commit()
        conn.close()

        return redirect("cart")
    

@app.route("/update_quantity", methods=["POST"])
def update_quantity():
    if request.method == "POST":
        product_id = request.form.get("product_id")
        quantity = request.form.get("quantity")

        # update quantity in the DB
        conn = get_database_connection()
        cur = conn.cursor()
        cur.execute ("UPDATE cart SET quantity = ? WHERE product_id = ?", (quantity, product_id))
        conn.commit()
        conn.close()
        return redirect("cart")


@app.route("/order", methods=["GET", "POST"])
def order():
    # 1. connect to DB
    conn = get_database_connection()
    cur = conn.cursor()
    if request.method == "GET":
        # get order history data - date, product, quantity, price
        history = cur.execute("""SELECT orders.created_at AS order_date, products.name AS product_name, order_item.quantity AS quantity, order_item.price AS price
            FROM orders
            JOIN order_item ON orders.id = order_item.order_id
            JOIN products ON order_item.product_id = products.id
            WHERE orders.user_id = ?
            ORDER BY order_date DESC;
            """, (session['user_id'],))
        return render_template("ordered.html", history=history)
    # if order button is clicked in cart page
    if request.method == "POST":
        # 2. check if user has enough cash to buy
        # total amount of products in the cart
        rows = cur.execute("""SELECT products.price, cart.quantity
            FROM products
            JOIN cart ON products.id = cart.product_id
            JOIN users ON cart.user_id = users.id
            WHERE users.id = ?""", (session['user_id'],)).fetchall()
        total_amount = 0
        for row in rows:
            total_amount += row['price'] * row['quantity']

        # check user cash
        row = cur.execute("SELECT cash FROM users WHERE id = ?;", (session["user_id"], )).fetchone()
        cash_left = row['cash'] - total_amount
        if cash_left < 0:
            error_msg = "Not enough cash!"
            conn.close()
            return render_template("cart.html", error_msg=error_msg)
        
        # 3. check if there is enough stock of the product
        rows_cart = cur.execute("SELECT * FROM cart WHERE user_id = ?", (session['user_id'],)).fetchall()
        for product in rows_cart:
            rows_stock = cur.execute("SELECT quantity FROM products WHERE id = ?", (product['product_id'],)).fetchone()
            #print(f"======= PROD QUANT: {product['quantity']} || STOCK: {rows_stock['quantity']} =======", file=sys.stderr)
            if product['quantity'] > rows_stock['quantity']:
                error_msg = "Lower the quantity of the product/s!"
                conn.close()
                return render_template("cart.html", error_msg=error_msg)
            
        # 4. change the stock in the shop for the bought products
        for product in rows_cart:
            rows_stock = cur.execute("SELECT quantity FROM products WHERE id = ?", (product['product_id'],)).fetchone()
            #print(f"======= PROD keys: {product.keys()} || STOCK: {rows_stock['quantity']} =======", file=sys.stderr)
            cur.execute("UPDATE products SET quantity = ? WHERE id = ?", (rows_stock['quantity'] - product['quantity'], product['product_id']))
            conn.commit()

        # 5. update users cash
        cur.execute("UPDATE users SET cash = ? WHERE id = ?", (cash_left, session['user_id']))
        conn.commit()

        # 6. add input to "order" table
        cur.execute("INSERT INTO orders (user_id, total_amount, status) VALUES (?, ?, ?)", (session['user_id'], total_amount, "bought"))
        conn.commit()

        # 7. add input to "order_item" table
        # get id of the latest order in table
        order = cur.execute("SELECT id FROM orders ORDER BY created_at DESC").fetchone()
        #print(f"****************** OBJECT = {rows_cart['product_id']} *******************", file = sys.stderr)
        for product in rows_cart:
            prod = cur.execute("SELECT price FROM products WHERE id = ?", (product['product_id'],)).fetchone()
            cur.execute("INSERT INTO order_item (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)", (order['id'], product['product_id'], product['quantity'], prod['price']))
            conn.commit()
        
        # 8. empty the current cart for the user
        cur.execute("DELETE FROM cart WHERE user_id = ?", (session['user_id'],))
        conn.commit()

        return redirect("order")