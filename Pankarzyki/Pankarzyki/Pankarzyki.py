# all the imports
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
render_template, flash
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
from datetime import date
from helpers import *


app = Flask(__name__)
app.config.from_object(__name__) # load config from this file

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'pankarzyki.db'),
    SECRET_KEY = 'secretkey',
    USERNAME = 'admin',
    PASSWORD = 'passw'
))
app.config.from_envvar('PANKARZYKI_SETTINGS', silent=True)

def init_db():
    db = get_db()
    with app.open_resource("schema.sql", mode = 'r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    #Initializes the databe.
    init_db()
    print('Initialized the database.')

def get_db():
    # Opens a new databes connection if there is none yet for
    # the current application context.
    if not hasattr(g, "sqlite_db"):
        g.sqlite_db = connect_db()
    return g.sqlite_db

def connect_db():
    # connects to a specific database
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

# draw the pairs and dates of matches, create a ligue schedule
def draft():
    #TO DO
    
    #db = get_db()
    #cur = db.cursor()
    # get all signed teams
    # TO DO cmd = 
    #cur.execute(cmd)
    #teams = cur.fetchall()
    # check if enough teams to play
    lenght = len(teams)
    if lenght < 2:
        db.close()
        return "Za mało ludzi. Sam/a chcesz grać?"
    # check how many team pairs to be matched in a single round in draft, rounded down
    pairs = int(lenght/2)

    # loop thru the teams to assign pairs and dates of the games
    for idx,row in enumerate(teams):
        # one date of the game for all in a same round
        round_date = idx * 7 +7

        pdx = 0
        # the idea is to connect in each round the first team from the list with the last one, than the second one with the one before the last and so on. pdx is the index watching to create only as many pairs as needed.
        # once the round is finished the main index idx makes all teams to be moved on the list by one position
        while pdx < pairs:
            first = 0+idx+pdx
            if first >= lenght:
                first -= lenght
            last = -1+idx-pdx

            cmd = "INSERT OR ABORT INTO {} (team1, team2, date) VALUES ({}, {}, date('now','+{} days'))" .format(ligue_schedule, teams[first]["rowid"], teams[last]["rowid"], round_date)
            try:
                cur.execute(cmd)
                pdx += 1
            except:
                db.close()
                return "bład zapisu wyniku losowania meczów"
    db.commit()
    db.close()


@app.route("/")
def index():
    return render_template("index.html")

# register user
@app.route("/register", methods=["GET", "POST"])
def register():

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            flash ("Jak się nie przedstawisz, to nie wpuszczę!")
            return render_template("register.html")

        # ensure password was submitted
        elif not request.form.get("password"):
            flash ("Hasło daj, bo nie wpuszczę!")
            return render_template("register.html")

        # make sure to repeat same password
        elif not request.form.get("password") == request.form.get("repeat password"):
            flash ("Takie samo hasło powtórz. Inaczej nie wpuszczę!")
            return render_template("register.html")

        #security check
        if seccheck(request.form.get("username")) == 0 or seccheck(request.form.get("password")) == 0 or seccheck(request.form.get("repeat password")) == 0:
            flash("Niepożądane znaki: \" ' `{};:[]()<> ")
            return render_template("register.html")

        # query database for username
        db = get_db()
        cur=db.cursor()
        cur.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"),))
        rows = cur.fetchall()

        # ensure username exists and password is correct
        if len(rows) >= 1:
            flash ("username already exists")
            return render_template("register.html")

        # insert new user into table
        try:
            cur.execute("INSERT INTO users (username, hash, user_div) \
                            VALUES (?,?,?)", \
                            (request.form.get("username"), \
                            pwd_context.encrypt(request.form.get("password")), \
                            (request.form.get("division"))))
            db.commit()
            db.close()
            flash ("Zakajetowane. Enjoy!")
            return redirect(url_for("login"))

        except RuntimeError:

            return "Error. Could not register"


    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        # query database for username
        db = get_db()
        cur=db.cursor()
        cur.execute("SELECT div_id, div_name FROM divisions")
        divs = cur.fetchall()
        db.close()

        return render_template("register.html", divs = divs)

# let user log into service
@app.route("/login", methods=["GET", "POST"])
def login():

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            flash ("Jak się nie przedstawisz, to nie wpuszczę!")
            return render_template("register.html")

        # ensure password was submitted
        elif not request.form.get("password"):
            flash ("Hasło daj, bo nie wpuszczę!")
            return render_template("register.html")

        #query database for username, check if exists and if password ok
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"),))
        rows = cur.fetchall()
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            flash ("Nie znamy się jeszcze, albo hasło nie pykło!")
            return render_template("login.html")

        #remember the user
        session["user_id"] = rows[0]["user_id"]
        session["username"] = rows[0]["username"]
        session["user_div"] = rows[0]["user_div"]

        return redirect(url_for("index"))

    #else if user reached route via GET (as by clicking link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("index"))

# let the user join to a ligue if there is open draft, if not offer the user to create one
@app.route("/join", methods=["GET", "POST"])
def join():
    if request.method == "POST":
        return render_template("join.html")
        
        

    if request.method == "GET":
        #check for recruiting ligues
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT *  FROM ligues JOIN users ON ligues.ligue_owner = users.user_id WHERE date('now') < date(ligues.start_date)")
        ligues = cur.fetchall()
        db.close()
        #display available ligues to join
        return render_template("join.html", ligues=ligues)

# let the user choose a partner and create a team
@app.route("/create_team", methods=["GET", "POST"])
def create_team():
    # when user reached this via POST (submitting the form)
    if request.method == "POST":
       return render_template("create_team.html")


    else:
        
        return render_template("create_team.html")


#create a new ligue according to user settings
@app.route("/create", methods=["GET", "POST"])
def create():

    # when user reached this via POST (submitting the form)
    if request.method == "POST":
        return render_template("create.html")

    else:
        return render_template("create.html")


@app.route("/calendar", methods=["GET", "POST"])
def calendar():

     # when user reached this via POST (submitting the form)
    if request.method == "POST":
        return render_template("calendar.html")

    else:
        
        return render_template("calendar.html")


@app.route("/results", methods=["GET", "POST"])
def results():
    return render_template("results.html")


