from flask import Blueprint, render_template
from app import app


# Main homepage
@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")

# Authenticaion routes
@app.route("/register")
def register():
    return render_template("/auth/register.html")


@app.route("/login")
def login():
    return render_template("/auth/login.html")
