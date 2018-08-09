import os
from flask import Flask, flash, redirect, render_template, request, session, url_for, g
from tempfile import mkdtemp
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import sqlite3
from functools import wraps
from multiprocessing import Value
from datetime import datetime

counter = Value('i', 0)
counter1 = Value('i', 0)

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS




# Configure files directory and allowed extensions
UPLOAD_FOLDER = 'static/photos'
UPLOAD_FOLDER_AVATAR = 'static/user-avatar'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
CATEGORIES = ["cars", "tech", "motors", "furniture", "entertainment", "clothing", "other"]


# Configure application
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_FOLDER_avatar'] = UPLOAD_FOLDER_AVATAR
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024


# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Connecting the sqlite3 database
DATABASE = 'buyit.db'


def get_db():
    """Connects the database"""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def insert(table, fields=(), values=()):
    """Inserts values into database"""
    cur = get_db()
    query = 'INSERT INTO %s (%s) VALUES (%s)' % (
        table,
        ', '.join(fields),
        ', '.join(['?'] * len(values))
    )
    cur.execute(query, values)
    cur.commit()
    # id = cur.lastrowid
    cur.close()
    return True
    # return id

@app.teardown_appcontext
def close_connection(exception):
    """Disconnects the database"""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    """Selects rows from the database"""
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


@app.route("/")
def index():
    """Show a list of items to buy"""
    items = query_db("SELECT * FROM items")
    return render_template("index.html", items = items, categories = CATEGORIES)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("mes.html", error = "must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("mes.html", error = "must provide password")

        # Query database for username
        rows = query_db("SELECT * FROM users WHERE user_name='%s';" % request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0][2], request.form.get("password")):
            return render_template("mes.html", error = "password is not currect")

        # Remember which user has logged in
        session["user_id"] = rows[0][0]
        print(rows)
        session["user_avatar"] =  rows[0][8]
        session["user_name"] =  request.form.get("username")
        print (session["user_avatar"])
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        

        avatar = request.files['avatar'] if request.files['avatar'] else "default.png"
        file_name = ""

        file_name = "%d.%s" %(counter1.value, avatar.filename.rsplit('.', 1)[1].lower())
        with counter1.get_lock():
            counter1.value += 1
            avatar.save(os.path.join("static/user-avatar", file_name))

        insert("users", ("user_name", "hash", "name", "last_name", "email", "country", "city", "avatars_dir"),
        (request.form.get("username"), generate_password_hash(request.form.get("password"),
        method='pbkdf2:sha256', salt_length=8), request.form.get("firstname"), request.form.get("surname"),
        request.form.get("email"), request.form.get("country"), request.form.get("city"), file_name))

        # redirect user to home page
        return redirect(url_for("index"))

    else:
        return render_template("register.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """add a listing to sell"""
    if request.method == "POST":
        photo = request.files['photo']
        file_name = ""

        if photo and allowed_file(photo.filename):
            file_name = "%d.%s" %(counter.value, photo.filename.rsplit('.', 1)[1].lower())
            with counter.get_lock():
                counter.value += 1
                photo.save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
                insert("items", ("user_id", "price", "name", "description", "photos_dir", "time", "lat", "lng", "category"), (session["user_id"], request.form.get("price"), request.form.get("title"), request.form.get("description"), file_name, str(datetime.now()), 0, 0, request.form.get("category")))

        return redirect(url_for("index"))
    
    else:
        return render_template("sell.html", categories = CATEGORIES)



@app.route("/items/<int:item_id>", methods=["GET", "POST"])
def item(item_id):
    """See information about the current item"""
    if request.method == "GET":
        item = query_db("SELECT * FROM items WHERE id=%d" %item_id)
        return render_template("item.html", item = item[0])


@app.route("/category/<category>", methods=["GET"])
def category(category):
    """get all the items that are from a specific category"""
    items = query_db("SELECT * FROM items WHERE category='%s'"%category)
    return render_template("index.html", items = items, categories = CATEGORIES)



@app.route("/search", methods=["GET"])
def search():
    """search for s specific item"""
    searchword = request.args.get('search', '')
    if not searchword:
        return render_template("mes.html", error = "must provide a search query")
    items = query_db("SELECT * FROM items WHERE name LIKE '%{}%'".format(searchword))
    return render_template("index.html", items = items, categories = CATEGORIES)