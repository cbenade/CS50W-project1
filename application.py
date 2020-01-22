import os
import re
import requests

from flask import Flask, flash, jsonify, render_template, redirect, request, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


##################################################################################################################
@app.route("/api/<isbn>")
def fetch_book_data(isbn):
    # Fetch book review data from Goodreads
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "dPdEyysah9rO8mGNMuAatw", "isbns": isbn})
    if not res:
        return jsonify({"error": "Invalid isbn number"}), 404
    review_count = res.json()["books"][0]["ratings_count"]
    average_score = res.json()["books"][0]["average_rating"]
    data = db.execute(
        "SELECT * FROM books JOIN authors ON authors.id = books.author_id WHERE isbn = :isbn",
        {"isbn": isbn}).fetchone()
    if not data:
        return jsonify({"error": "Isbn number not in database"}), 404
    return jsonify({
        "title": data["title"],
        "author": data["name"],
        "year": data["year"],
        "isbn": isbn,
        "review_count": review_count,
        "average_score": average_score
        })

##################################################################################################################
@app.route("/")
@login_required
def index():
    return render_template("index.html")

##################################################################################################################
@app.route("/login", methods=["GET", "POST"])
def login():
    # Clear user id
    session.clear()
    # User requested page via POST
    if request.method == "POST":
        # Verify that form fields are not blank
        if not request.form.get("username"):
            flash('username field blank')
        elif not request.form.get("password"):
            flash('password field blank')
        else:
            # Attempt login
            db_result = db.execute("SELECT * FROM users WHERE username = :username", 
                {"username": request.form.get("username")}).fetchone()
            if db_result == None:
                flash("user not found in database")
            else:
                # Check that password is correct
                if check_password_hash(db_result["hash"], request.form.get("password")):
                    # Login user and direct to index route
                    session["user_id"] = db_result["id"]
                    return redirect("/")
                else:
                    flash("incorrect username/password combination")
        return render_template("login.html")
    # User requested page via GET
    else:
        return render_template("login.html")

##################################################################################################################
@app.route("/logout")
@login_required
def logout():   
    # Clear user id
    session.clear()
    # Redirect to login page
    return redirect('/login')

##################################################################################################################
@app.route("/register", methods=["GET", "POST"])
def register():
    # User requested page via POST
    if request.method == "POST":
        # Verify that form fields are not blank
        if not request.form.get("username"):
            flash('username field blank')
        elif not request.form.get("password1") or not request.form.get("password2"):
            flash('password field(s) blank')
        elif request.form.get("password1") != request.form.get("password2"):
            flash('passwords do not match')
        else:
            # Check that username is not taken
            db_result = db.execute("SELECT username FROM users WHERE username = :username", 
                {"username": request.form.get("username")}).fetchone()
            if db_result == None:
                # Hash password
                pass_hash = generate_password_hash(request.form.get("password1"), 
                    method='pbkdf2:sha256', salt_length=8)
                # Register username and hash
                db.execute(
                    "INSERT INTO users (username, hash) VALUES (:username, :hash)", 
                    {"username": request.form.get("username"), "hash": pass_hash})        
                db.commit()
                flash(f'''registered user \"{request.form.get("username")}\" with 
                      password \"{request.form.get("password1")}\"''')
            else:
                # Notify user that username is taken
                flash('that username is taken')            
        return render_template("register.html")
    # User requested page via GET
    else:
        return render_template("register.html")

##################################################################################################################
@app.route("/search", methods=["GET", "POST"])
@login_required
def search():   
    # User requested page via POST
    if request.method == "POST":
        # Verify that search field not empty
        if not request.form.get("search"):
            flash('search field blank')
            return redirect('/')
        # Retrieve book data from database
        search_string = request.form.get("search").lower()
        data = db.execute("SELECT * FROM books JOIN authors ON authors.id = books.author_id").fetchall()
        # Create regex object
        pattern = re.compile(search_string)
        # Search isbn numbers, book titles, and author names for matches
        matches = []
        for book in data:
            isbn_result = pattern.search(book["isbn"].lower())
            title_result = pattern.search(book["title"].lower())
            author_result = pattern.search(book["name"].lower())
            if isbn_result != None or title_result != None or author_result != None:
                matches.append({
                    "isbn": book["isbn"],
                    "title": book["title"],
                    "author": book["name"]
                })  
        # Sort matches by book title, author name
        matches = sorted(matches, key = lambda i: (i['title'], i['author']))
        return render_template("search.html", search_string=request.form.get("search"), results=matches)  
    # User requested page via GET
    else:
        return redirect('/')

##################################################################################################################
@app.route("/search/<isbn>", methods=["GET", "POST"])
@login_required
def search_book(isbn):   
    # User requested page via POST
    if request.method == "POST":
        # Check if user has already submitted review for that book
        db_result = db.execute(
            "SELECT * FROM reviews WHERE book_id = :book_id AND user_id = :user_id",
            {"book_id": isbn, "user_id": str(session["user_id"])}).fetchone()
        if db_result != None:
            # Delete previous review from database
            db.execute(
                "DELETE FROM reviews WHERE book_id = :book_id AND user_id = :user_id",
                {"book_id": isbn, "user_id": str(session["user_id"])})
        # Insert new review to database
        db.execute(
            "INSERT INTO reviews (book_id, user_id, rating, text) VALUES (:book_id, :user_id, :rating, :text)",
            {"book_id": isbn, "user_id": str(session["user_id"]), 
            "rating": request.form.get("rating"), "text": request.form.get("text")})        
        db.commit()
        return redirect("/search/" + isbn)
    # User requested page via GET
    else:
        # Retrieve book info from api
        res = requests.get("http://127.0.0.1:5000/api/" + isbn)
        if not res:
            return "Error, invalid isbn number"
        data = res.json()
        # Retrieve book reviews from database
        db_result = db.execute(
            "SELECT * FROM reviews JOIN users ON users.id = reviews.user_id WHERE book_id = :book_id",
            {"book_id": data["isbn"]}).fetchall()
        # Format database data into list of dictionaries
        reviews = []
        if len(db_result) > 0:
            for review in db_result:
                reviews.append({
                    "id": review["id"],
                    "username": review["username"],
                    "rating": review["rating"],
                    "text": review["text"]
                })
        # Sort reviews by id in reverse order
        reviews = sorted(reviews, key = lambda i: i['id'], reverse=True)    
        # Add reviews to data
        data["reviews"] = reviews
        return render_template("book_info.html", data=data)
