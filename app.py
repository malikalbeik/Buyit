"""
This is app.py the main file for flask to run.
Here all the routes of the app are defined and setup.
"""
import os
import uuid
from datetime import datetime
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from flask import Flask, redirect, flash, render_template, request, session, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from helpers import login_required, allowed_file
from config import Config




# Configure application from config.py
app = Flask(__name__) # pylint: disable=invalid-name
app.config.from_object(Config)
db = SQLAlchemy(app)  # pylint: disable=invalid-name
migrate = Migrate(app, db)  # pylint: disable=invalid-name
Session(app)

from models import User, Item, Notification  # pylint: disable=C0413

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    """Disable caches"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.teardown_appcontext
def shutdown_session(exception=None):  # pylint: disable=w0613
    """executed every time the application context tears down"""
    db.session.remove()


@app.route("/")
def index():
    """Show a list of items to buy"""
    items = Item.query.filter(not Item.sold).limit(8).all()
    return render_template("index.html", \
        categories=app.config['CATEGORIES'], \
        items_class="items", items=items)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        password = request.form.get("password")

        # Ensure username was submitted
        if not password:
            return render_template("mes.html", error="must provide username")

        # Ensure password was submitted
        if not request.form.get("password"):
            return render_template("mes.html", error="must provide password")

        # Query database for username
        user = User.query.filter(User.username == request.form.get("username")).first_or_404()

        # Ensure username exists and password is correct
        if not check_password_hash(user.hash, request.form.get("password")):
            return render_template("mes.html", error="password is not currect")

        # Remember which user has logged in
        session["user_id"] = user.id
        session["user_avatar"] = user.avatar
        session["user_name"] = user.username
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

        user = User(username=request.form.get("username"), \
            hash=generate_password_hash(request.form.get("password"), \
            method='pbkdf2:sha256', salt_length=8), \
            email=request.form.get("email"), firstname=request.form.get("firstname"), \
            lastname=request.form.get("lastname"), country=request.form.get("country"), \
            state=request.form.get("state"), city=request.form.get("city"), avatar=file_name)
        db.session.add(user)
        db.session.commit()

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
        user = User.query.filter(User.id == session["user_id"]).first_or_404()

        if photo and allowed_file(photo.filename):
            file_name = "%d.%s" %(uuid.uuid4(), photo.filename.rsplit('.', 1)[1].lower())
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))


            new_item = Item(user_id=session["user_id"], \
                price=request.form.get("price"), \
                title=request.form.get("title"), description=request.form.get("description"), \
                photo=file_name, category=request.form.get("category"), country=user.country, \
                state=user.state, city=user.city)
            db.session.add(new_item)
            db.session.commit()

        return redirect(url_for("index"))
    return render_template("sell.html", categories=app.config['CATEGORIES'])



@app.route("/items/<int:item_id>", methods=["GET"])
def item(item_id):
    """See information about the current item"""
    current_item = Item.query.filter(Item.id == item_id).first_or_404()
    if not current_item:
        return render_template("mes.html", error="there is no such item")
    if current_item.sold:
        return render_template("mes.html", \
            error="the item that you are looking for is already sold")
    return render_template("item.html", item=current_item)


@app.route("/category/<cat>", methods=["GET"])
def category(cat):
    """get all the items that are from a specific category"""
    items = Item.query.filter(Item.category == cat and Item.sold == 0).limit(8).all()
    return render_template("index.html", items_class=cat, \
        categories=app.config['CATEGORIES'], items=items)



@app.route("/search", methods=["GET"])
def search():
    """search for s specific item"""
    searchword = request.args.get('search', '')
    json = request.args.get('json', '')

    if not json:
        if not searchword:
            return render_template("mes.html", error="must provide a search query")
        items = Item.query.filter(
            (Item.title.like("%{}%".format(searchword))) & (not Item.sold)).all()
        return render_template("index.html", items=items, categories=app.config['CATEGORIES'])
    if not searchword:
        return 0
    items = Item.query.filter(
        Item.title.like(("%{}%".format(searchword))) & (not Item.sold)).all()
    response = jsonify(items)
    response.status_code = 200
    return response


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """Show the user information and let the user change it """
    user = User.query.get(session["user_id"])
    if request.method == "GET":
        return render_template("profile.html", user=user)
    user.firstname = request.form.get("firstname")
    user.lastname = request.form.get("lastname")
    user.email = request.form.get("email")
    db.session.commit()

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
        items = Item.query.filter(not Item.sold).limit(limit).offset(offset).all()
    else:
        items = Item.query.filter(
            (Item.category == categ) & (not Item.sold)).limit(limit).offset(offset).all()
    response = jsonify(items)
    response.status_code = 200
    return response


@app.route("/buy/<int:item_id>", methods=["GET"])
@login_required
def buy(item_id):
    """lets the user buys a specific item"""
    item_to_buy = Item.query.get(item_id)
    if not item_to_buy:
        return render_template("mes.html", error="there is no such item")
    if item_to_buy.sold:
        return render_template("mes.html", \
        error="the item that you are trying to buy is already sold")
    if item_to_buy.user_id == session['user_id']:
        return render_template("mes.html", error="you can't buy your own item.")
    notification = Notification(
        user_id=item_to_buy.user_id, item_id=item_to_buy.id)
    db.session.add(notification)
    item.sold = True
    item.buying_user = session["user_id"]
    db.session.commit()
    return render_template("mes.html", error="items bought successfully")


@app.route("/currentsellings", methods=["GET"])
@login_required
def currentsellings():
    """shows a list of the ites that the user is currently selling"""
    items = Item.query.filter((Item.user_id == session["user_id"]) & (not Item.sold)).all()
    return render_template("currentsellings.html", items=items)


@app.route("/item/edit/<int:item_id>", methods=["GET", "POST"])
@login_required
def edit(item_id):
    """lets the user edit his currently selling items"""
    item_to_edit = Item.query.get(item_id)
    if not item_to_edit:
        return render_template("mes.html", error="page not found")
    if item_to_edit.user_id != session['user_id']:
        return render_template("mes.html", \
        error="you don't own the item that you are trying to edit")
    if request.method == "GET":
        return render_template("edit.html", item=item_to_edit, categories=app.config['CATEGORIES'])
    if not request.form.get("photo"):
        item_to_edit.title = request.form.get("title")
        item_to_edit.price = request.form.get("price")
        item_to_edit.description = request.form.get("description")
        item_to_edit.category = request.form.get("category")
    else:
        os.remove(app.config['UPLOAD_FOLDER']/item_to_edit.photos_dir)
        photo = request.files['photo']
        file_name = ""

        if photo and allowed_file(photo.filename):
            file_name = "%d.%s" %(uuid.uuid4(), photo.filename.rsplit('.', 1)[1].lower())
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))

            item_to_edit.photo = file_name
    db.session.commit()
    return redirect(url_for("currentsellings"))


@app.route("/delete/<int:item_id>", methods=["GET"])
@login_required
def delete(item_id):
    """delete an item from the database"""
    item_to_delete = Item.query.get(item_id)
    if item_to_delete and item_to_delete.user_id == session['user_id']:
        db.session.delete(item_to_delete)
        db.session.commit()
        flash('You have successfully deleted the item')
        return redirect(url_for("currentsellings"))
    return render_template("mes.html", \
    error="there has been an error deleting this item please try again later")


@app.route("/history", methods=["GET"])
@login_required
def history():
    """shows a list of the users purchases"""
    items = Item.query.filter(Item.buying_user == session['user_id']).all()
    return render_template("history.html", items=items)


@app.route("/history/items/<int:item_id>", methods=["GET"])
@login_required
def purchased_item(item_id):
    """shows information about the pruchased items"""
    current_item = Item.query.get(item_id)
    if current_item and current_item.buying_user == session['user_id']:
        return render_template("purchased_item.html", item=current_item)
    if current_item.buying_user != session['user_id']:
        return render_template("mes.html", error="you don't have permession to access this page")
    return render_template("mes.html", error="an error accord please try again later")


@app.route("/notifications", methods=["GET"])
@login_required
def notifications():
    """lets the user see his latest sellings"""
    selling_notifications = db.session.query(
        Notification, Item.title).join(Item).filter(Notification.user_id == session['user_id'])\
        .all()
    return render_template("notifications.html", notifications=selling_notifications)


@app.template_filter('strftime')
def _jinja2_filter_datetime(date):
    native = date.replace(tzinfo=None)
    dateformat = '%b %d, %Y'
    if native.strftime(dateformat) == str(datetime.now().strftime('%b %d, %Y')):
        return "Today"
    return native.strftime(dateformat)
