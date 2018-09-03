"""
This is app.py the main file for flask to run.
Here all the routes of the app are defined and setup.
"""
import os
from datetime import datetime
from multiprocessing import Value
from tempfile import mkdtemp
from flask_session import Session
import uuid
from werkzeug.security import check_password_hash, generate_password_hash
from flask import Flask, redirect, flash, render_template, request, session, url_for, jsonify, abort
from helpers import login_required, allowed_file, insert, query_db, close_connection, update
from dateutil import parser



# Configure files directory and allowed extensions
UPLOAD_FOLDER = 'static/photos'
UPLOAD_FOLDER_AVATAR = 'static/user-avatar'
CATEGORIES = ["cars", "tech", "motors", "furniture", "entertainment", "clothing", "other"]


# Configure application
app = Flask(__name__) # pylint: disable=invalid-name
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_FOLDER_avatar'] = UPLOAD_FOLDER_AVATAR
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024


# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    """Disable caches"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)



@app.teardown_appcontext
def teardown_appcontext(exception):
    """close sqlite connection when a teardown happens"""
    close_connection()
    return exception


@app.route("/")
def index():
    """Show a list of items to buy"""
    items = query_db("SELECT * FROM items WHERE sold=0 LIMIT 8 ")
    return render_template("index.html", categories=CATEGORIES, items_class="items", items=items)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        password = request.form.get("username")

        # Ensure username was submitted
        if not password:
            return render_template("mes.html", error="must provide username")

        # Ensure password was submitted
        if not request.form.get("password"):
            return render_template("mes.html", error="must provide password")

        # Query database for username
        rows = query_db("SELECT * FROM users WHERE user_name='%s';" % password)[0]

        # Ensure username exists and password is correct
        if not check_password_hash(rows['hash'], request.form.get("password")):
            return render_template("mes.html", error="password is not currect")

        # Remember which user has logged in
        session["user_id"] = rows['id']
        session["user_avatar"] = rows['avatars_dir']
        session["user_name"] = password
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        avatar = request.files['avatar'] if request.files['avatar'] else "default.png"
        file_name = ""

        file_name = "%d.%s" %(uuid.uuid4(), avatar.filename.rsplit('.', 1)[1].lower())
        avatar.save(os.path.join("static/user-avatar", file_name))

        insert("users", ("user_name", "hash", "name", "last_name", \
        "email", "country", "city", "avatars_dir"), (
            request.form.get("username"), \
            generate_password_hash(request.form.get("password"), \
            method='pbkdf2:sha256', salt_length=8), \
            request.form.get("firstname"), \
            request.form.get("surname"), \
            request.form.get("email"), \
            request.form.get("country"), \
            request.form.get("city"), file_name))

        # redirect user to home page
        return redirect(url_for("index"))
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
            file_name = "%d.%s" %(uuid.uuid4(), photo.filename.rsplit('.', 1)[1].lower())
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
            insert("items", (
                "user_id", "price", "name", "description", \
                "photos_dir", "time", "category"), (
                    session["user_id"], request.form.get("price"), \
                    request.form.get("title"), request.form.get("description"), \
                    file_name, str(datetime.now()), request.form.get("category")))

        return redirect(url_for("index"))
    return render_template("sell.html", categories=CATEGORIES)



@app.route("/items/<int:item_id>", methods=["GET"])
def item_page(item_id):
    """See information about the current item"""
    item = query_db("SELECT * FROM items WHERE id=%d" %item_id)
    if not item:
        return render_template("mes.html", error="there is no such item")
    elif item[0]["sold"] == 1:
        return render_template("mes.html", error="the item that you are looking for is already sold")
    return render_template("item.html", item=item[0])


@app.route("/category/<cat>", methods=["GET"])
def category(cat):
    """get all the items that are from a specific category"""
    items = query_db("SELECT * FROM items WHERE category='{}' and sold=0 LIMIT 8 ".format(cat))
    return render_template("index.html", items_class=cat, categories=CATEGORIES, items=items)



@app.route("/search", methods=["GET"])
def search():
    """search for s specific item"""
    searchword = request.args.get('search', '')
    json = request.args.get('json', '')

    if not json:
        if not searchword:
            return render_template("mes.html", error="must provide a search query")
        items = query_db("SELECT * FROM items WHERE name LIKE '%{}%' and sold=0".format(searchword))
        return render_template("index.html", items=items, categories=CATEGORIES)
    if not searchword:
        return 0
    items = query_db("SELECT name FROM items WHERE name LIKE '%{}%' and sold=0".format(searchword))
    response = jsonify(items)
    response.status_code = 200
    return response


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """Show the user information and let the user change it """
    if request.method == "GET":
        user = query_db("SELECT * FROM users WHERE id={}".format(session["user_id"]))[0]
        return render_template("profile.html", user=user)
    update('users', 'id = {}'.format(session["user_id"]), (
        'name', 'last_name', 'email'), ( \
            request.form.get("firstname"), \
            request.form.get("lastname"), \
            request.form.get("email")))
    flash('You have successfully updated your information')
    return redirect(url_for('profile'))


@app.route("/about", methods=["GET"])
def about():
    """Shows information about the app and explains its purpose"""
    return render_template("about.html")


@app.route("/getelements", methods=["GET"])
def getelements():
    """gets a number of elements from the database and returns them as a json response"""
    offset = request.args.get('offset', '')
    limit = request.args.get('limit', '')
    categ = request.args.get('category', '')

    if not limit or not offset:
        return render_template(
            "mes.html",
            error="please provide a limit and an offset for your request to be made."
            )
    if not categ:
        items = query_db("SELECT * FROM items WHERE sold=0 LIMIT {} OFFSET {}".format(limit, offset))
    else:
        items = query_db(
            "SELECT * FROM items WHERE category = '{}' and sold=0 LIMIT {}, {} ".format(categ, offset, limit))
    response = jsonify(items)
    response.status_code = 200
    return response


@app.route("/buy/<int:id>", methods=["GET"])
@login_required
def buy(id):
    """lets the user buys a specific item"""
    item = query_db("SELECT * FROM items WHERE id=%d" %id)
    if not item:
        return render_template("mes.html", error="there is no such item")
    elif item[0]["sold"] == 1:
        return render_template("mes.html", error="the item that you are trying to buy is already sold")
    update('items', 'id = {}'.format(id), ('sold', 'buying_user'), (1, session["user_id"]))
    return render_template("mes.html", error="items bought successfully")


@app.route("/currentsellings", methods=["GET"])
@login_required
def currentsellings():
    """shows a list of the ites that the user is currently selling"""
    items = query_db("SELECT * FROM items WHERE user_id=%d and sold=0" %session["user_id"])
    return render_template("currentsellings.html", items=items)


@app.route("/item/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    """lets the user edit his currently selling items"""
    item = query_db("SELECT * FROM items WHERE id=%d" %id)
    if not item:
        return render_template("mes.html", error="page not found")
    elif item[0]['user_id'] != session['user_id']:
        return render_template("mes.html", error="you don't own the item that you are trying to edit")
    if request.method == "GET":
        return render_template("edit.html", item=item[0],  categories=CATEGORIES)
    else:
        if not request.form.get("photo"):
            update('items', 'id = {}'.format(id), (
            'name', 'price', 'description', 'category'), ( \
                request.form.get("name"), \
                request.form.get("price"), \
                request.form.get("description"), \
                request.form.get("category")))
        else:
            os.remove(UPLOAD_FOLDER/item["photos_dir"])
            photo = request.files['photo']
            file_name = ""

            if photo and allowed_file(photo.filename):
                file_name = "%d.%s" %(uuid.uuid4(), photo.filename.rsplit('.', 1)[1].lower())
                photo.save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))

                update('items', 'id = {}'.format(id), 'photos_dir', file_name)
        return redirect(url_for("currentsellings"))


@app.template_filter('strftime')
def _jinja2_filter_datetime(date, fmt=None):
    date = parser.parse(date)
    native = date.replace(tzinfo=None)
    format='%b %d, %Y'
    if native.strftime(format) == str(datetime.now().strftime('%b %d, %Y')):
        return "Today"
    return native.strftime(format) 