### paracord-online-store (repository)
# Knotted Shop (project title)
#### Video Demo:  https://youtu.be/KGDMZaLoeJM
#### Description:
I wanted to create a web store that sells handmade paracord bracelets. The nameI choose for this project is "Knotted Shop" (because bracelet is made of knots :) )

## layout.html
First thing I did is create a basic layout for my website. At the top I incorporated the links needed, for example bootstrap library...
Next I did was a "title" block which I changed on each of my pages.
In the body I created a navigation menu with "home" and "bracelets" items for which you don't need to be logged in or registered. On the right side of nav menu, you have the ability to log in or register for an account.

if a session is active (user is logged in), then additional items appear in the menu on the right side: cart, my profile, my orders, log out.

For the main part of the page I also created a block "main" where all the stuff will go on the other pages.

## database
Next thing I did was create a database tables which I needed at the moment (users and products)

This is their schema:
'''
CREATE TABLE users (
id INTEGER PRIMARY KEY NOT NULL UNIQUE,
first_name TEXT NOT NULL,
last_name TEXT NOT NULL,
username TEXT NOT NULL UNIQUE,
hash TEXT NOT NULL,
email TEXT NOT NULL UNIQUE,
address_id INTEGER,
last_login_date DATE, cash INTEGER DEFAULT 1000);

CREATE TABLE products (
id INTEGER PRIMARY KEY NOT NULL UNIQUE,
name TEXT NOT NULL,
descr TEXT,
price INTEGER NOT NULL,
quantity INTEGER NOT NULL);
'''
I had some problems with connecting and working with the database but I solved it after some time, because it's a bit different when working in CS50 codespace or in my own local repository

## registration.html
Then I went and worked on registration. Also everytime I added a new html page I also worked on my Python code. when creating this page I created the ability to register a new user, save it's data in the database and I also made some conditional statements that check if username and email already exist in the db, if all the fields are filled with text and if something was not right a created and displayed an error message regarding the problem that they have. For password hashing I used "werkzeug" sha256 method.

## login.html and logout
When user registers successfully he is redirected to login page where he can then log in with his username and password. All input fields are checked if they are empty etc. program queries the inputed username and checks if password is correct. If yes, then user id is stored in session which is later used in almost every function I have, so I can associate what user is doing on the website (ordered products, current balance,...). When login is successful, user is redirected to the home page (index.html). When a user finishes everything he wants he can log out, the session is cleared and user is redirected again to login.html

## index.html
Home page is nothing special. It has an information about project name, my name, date and that's it.

## profile.html
when profile page is displayed, user sees all his information that is stored in the db.
User has the ability to change his data. Data is changed via POST (request.form.get function). The app detects which fields have some text in them and that data is then updated in the db. If no text is in the input fields, the data stays the same.

## products.html
This page displays all the products in the database. Information displayed is: name, description, price and curent stock. At this point I also uploaded 3 product photos in the static folder, and renamed the photos that the id of the product is the name of the photo, which I then used to display the photos on the page using id from the db.
With this page I also used JavaScript to add items to the cart. I linked the file in static folder (script.js) in the beginning of the main block in html

## script.js 
This script detects if a button "add to cart" is clicked on the page. When the button is clicked i created a function that handles adding items to the cart. The function gets information from the products, which is linked with the tag attribute "data-product-id, data-product-name,..." and the data is then sent to this script. The script also checks if the product is in stock and if not it shows an alert. Otherwise, data is sent in an object via AJAX request to Flask, to add the item to the cart (adds the item to the DB) and if the data is sent successfully it displays an alert that the item is added to the cart.

At this point in time I also added 3 new tables to my DB:
'''
CREATE TABLE cart (
id INTEGER PRIMARY KEY NOT NULL UNIQUE,
user_id INTEGER NOT NULL,
product_id INTEGER NOT NULL,
quantity INTEGER NOT NULL,
created_at DATE NOT NULL,
is_ordered INTEGER);

CREATE TABLE IF NOT EXISTS "orders" (
id INTEGER PRIMARY KEY UNIQUE,
user_id INTEGER,
total_amount INTEGER,
status TEXT,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);

CREATE TABLE order_item (
    id INTEGER PRIMARY KEY,
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    price DECIMAL,
    FOREIGN KEY (order_id) REFERENCES "order"(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);
'''
"cart" table: stores information about the products that user wants to buy and how many of those products he wants to buy

"orders" table: stores information about the order user makes. Which user bought the items, at what total price and when

"order_item" table: stores information about each of the products bought that is displayed in "My Orders" page. (date & time of the purchase, what product, quantity and at what price was the product bought)

In python file, the data from the AJAX request is received as JSON and is parsed accordingly that the database is up to date if maybe user clicked twice on the "add to cart" the quantity is increased by 1.

## cart.html
This page displays the products in users cart (name, quantity and price). There is ability to remove items from cart or to change the quantity. Every change that is made to the cart is also updated in the DB. Bellow this information users see the total amount to pay and their current cash available. If user has more than 1 product and wants to change the quantity of products, he has to update the quantity one at a time.

When "Remove" is clicked the productid is sent to python to delete the product from the cart via POST and then it redirects the user back to cart.

When "update" quantity is clicked current id of the product and quantity is sent to python to update the quantity in the cart and then it is also displayed correctly on the page.

When "order now" is clicked program first checks if the user has enough cash to buy via sql query with sessions user id is used conditional. Then if there is enough cash, the stock of the product is checked again in db. If this is also ok, the stock is reduced by the number of bought products from the user. User cash is updated and an input is added to the "order" and "order_item" table. In the end the current cart is emptied and the user is redirected to "My orders"