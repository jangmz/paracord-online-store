import os
from flask import Flask, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
#app.config["SESSION_PERMANENT"] = False
#app.config["SESSION_TYPE"] = "filesystem"
#session(app)

#@app.after_request
#def after_request(response):
"""Ensure responses aren't cached"""
    #response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    #response.headers["Expires"] = 0
    #response.headers["Pragma"] = "no-cache"
    #return response

@app.route("/")
def index():
    return "<p> Hello World! <p>"

#@app.route("/registration")
#def registration():
    #return render_template ("registration.html")